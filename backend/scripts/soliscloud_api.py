import requests
import hmac
import hashlib
import time
import json
import logging
import os
import sys
import base64
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from io import TextIOWrapper
from typing import Any, List, Dict, Optional
from pytz import timezone
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging with date-based filename
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_date = datetime.now(timezone('Asia/Kolkata')).strftime('%Y%m%d')  # IST date
log_file = os.path.join(log_dir, f'soliscloud_api_{log_date}.log')

# Verify file writability
try:
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Log file initialized at {datetime.now(timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S IST')}\n")
except Exception as e:
    print(f"Failed to verify log file writability: {e}", file=sys.stderr)

stream_handler = logging.StreamHandler(stream=TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'),
        stream_handler
    ]
)
logger = logging.getLogger(__name__)

class SolisCloudAPI:
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://www.soliscloud.com:13333", rate_limit_delay: float = 0.6):
        self.api_key = api_key.strip()
        self.api_secret = api_secret.strip()
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay

    def set_rate_limit_delay(self, delay: float):
        """Adjust rate limit delay dynamically."""
        self.rate_limit_delay = max(0.1, delay)  # Minimum 0.1s
        logger.info(f"Rate limit delay set to {self.rate_limit_delay}s")

    def generate_signature(self, method: str, path: str, content_md5: str, content_type: str, date: str) -> str:
        canonical_content_type = content_type.split(';')[0]
        canonical_string = f"{method}\n{content_md5}\n{canonical_content_type}\n{date}\n{path}"
        logger.debug(f"Canonical string for signature: {canonical_string}")
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            canonical_string.encode('utf-8'),
            hashlib.sha1
        ).digest()
        return base64.b64encode(signature).decode('utf-8')

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Optional[Dict]:
        endpoint = endpoint.lstrip("/")
        path = f"/v1/api/{endpoint}"
        content_type = "application/json;charset=UTF-8"

        timestamp = str(int(time.time()))
        date_header = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        payload_str = json.dumps(payload or {}, separators=(',', ':'))
        content_md5 = base64.b64encode(hashlib.md5(payload_str.encode('utf-8')).digest()).decode('utf-8')
        signature = self.generate_signature(method, path, content_md5, content_type, date_header)

        headers = {
            "Content-Type": content_type,
            "Authorization": f"API {self.api_key}:{signature}",
            "Timestamp": timestamp,
            "Date": date_header,
            "Content-MD5": content_md5
        }
        safe_headers = {k: ("***" if k == "Authorization" else v) for k, v in headers.items()}
        logger.debug(f"Making {method} request to {self.base_url}{path} with headers: {safe_headers} and payload: {payload}")

        try:
            response = requests.request(method, f"{self.base_url}{path}", headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Response from {endpoint}: {data}")

            if not data.get("success") or data.get("code") != "0":
                error_msg = data.get("msg", "Unknown error")
                error_code = data.get("code", "Unknown")
                logger.error(f"API error for {endpoint}: {error_msg} (code: {error_code})")
                return None

            time.sleep(self.rate_limit_delay)
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {str(e)}")
            return None

    def get_all_stations(self, user_id: str, username: str = None, password: str = None) -> List[Dict[str, Any]]:
        page_no = 1
        page_size = 100
        all_stations = []

        while True:
            params = {"pageNo": page_no, "pageSize": page_size}
            response = self.make_request("POST", "userStationList", params)
            if not response:
                logger.error(f"Station list request failed for page {page_no}")
                break

            data = response.get("data", {})
            stations = data.get("page", {}).get("records", [])
            for station in stations:
                create_date = station.get("createDate", 0)
                if isinstance(create_date, (int, float)):
                    create_date = datetime.fromtimestamp(create_date / 1000, tz=timezone('UTC')).strftime('%Y-%m-%d')
                station_data = {
                    "station_id": station.get("id", ""),
                    "plant_name": station.get("stationName", "Unknown"),
                    "capacity": float(station.get("capacity", 0.0)),
                    "install_date": create_date,
                    "time_zone": float(station.get("timeZone", 5.5))
                }
                if station_data["station_id"]:
                    all_stations.append(station_data)
                else:
                    logger.warning(f"Skipping station with missing ID: {station}")

            total_records = data.get("page", {}).get("total", 0)
            logger.info(f"Fetched {len(stations)} stations on page {page_no}. Total: {total_records}")
            if page_no * page_size >= total_records:
                break
            page_no += 1

        logger.info(f"Fetched a total of {len(all_stations)} stations")
        return all_stations

    def get_all_inverters(self, user_id: str, username: str = None, password: str = None, station_id: str = None) -> List[Dict[str, Any]]:
        page_no = 1
        page_size = 100
        all_inverters = []

        while True:
            params = {"stationId": station_id, "pageNo": page_no, "pageSize": page_size}
            response = self.make_request("POST", "inverterList", params)
            if not response:
                logger.error(f"Inverter list request failed for station {station_id}, page {page_no}")
                break

            data = response.get("data", {})
            inverters = data.get("page", {}).get("records", [])
            for inverter in inverters:
                inverter_id = inverter.get("id", "")
                inverter_sn = inverter.get("sn", "")
                if not inverter_id or not inverter_sn:
                    logger.warning(f"Skipping invalid inverter: ID={inverter_id}, SN={inverter_sn}")
                    continue
                inverter_data = {
                    "id": inverter_id,
                    "sn": inverter_sn,
                    "inverter_model": inverter.get("model", "Unknown"),
                    "panel_model": "Unknown",
                    "pv_count": inverter.get("pvCount", 0),
                    "string_count": inverter.get("stringCount", 0),
                    "first_install_date": inverter.get("installDate", "1970-01-01")
                }
                all_inverters.append(inverter_data)

            total_records = data.get("page", {}).get("total", 0)
            logger.info(f"Fetched {len(inverters)} inverters for station {station_id} on page {page_no}. Total: {total_records}")
            if page_no * page_size >= total_records:
                break
            page_no += 1

        logger.info(f"Fetched a total of {len(all_inverters)} inverters for station {station_id}")
        return all_inverters

    def get_inverter_real_time_data(self, user_id: str, username: str = None, password: str = None, device: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not device or not device.get("id") or not device.get("sn"):
            logger.error("Invalid device data provided")
            return []

        params = {"id": device["id"], "sn": device["sn"]}
        response = self.make_request("POST", "inverterDetail", params)
        if not response:
            logger.warning(f"No real-time data for device {device['sn']}")
            return []

        data = response.get("data", {})
        if not isinstance(data, dict):
            logger.error(f"Unexpected data format for device {device['sn']}: {data}")
            return []

        timestamp_ms = int(data.get("dataTimestamp", 0))
        entry = {
            "timestamp": datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S') if timestamp_ms else datetime.now(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S'),
            "total_power": float(data.get("pac", 0.0)),
            "energy_today": float(data.get("eToday", 0.0)),
            "pr": float(data.get("pr", 0.0)),
            "state": str(data.get("state", "unknown")),
            "r_voltage": float(data.get("uAc1", 0.0)),
            "s_voltage": float(data.get("uAc2", 0.0)),
            "t_voltage": float(data.get("uAc3", 0.0)),
            "r_current": float(data.get("iAc1", 0.0)),
            "s_current": float(data.get("iAc2", 0.0)),
            "t_current": float(data.get("iAc3", 0.0)),
        }
        for i in range(1, 13):
            entry[f"pv{i:02d}_voltage"] = float(data.get(f"uPv{i}", 0.0))
            entry[f"pv{i:02d}_current"] = float(data.get(f"iPv{i}", 0.0))

        logger.info(f"Fetched real-time data for device {device['sn']}")
        return [entry]

    def get_inverter_historical_data(self, user_id: str, username: str = None, password: str = None, device: Dict[str, Any] = None, start_date: str = None, end_date: str = None, station_id: str = None) -> List[Dict[str, Any]]:
        if not device or not device.get("id") or not device.get("sn"):
            if station_id:
                inverters = self.get_all_inverters(user_id, station_id=station_id)
                if inverters:
                    device = inverters[0]
                    logger.info(f"Auto-fetched inverter: ID={device['id']}, SN={device['sn']}")
                else:
                    logger.error(f"No inverters found for station {station_id}")
                    return []
            else:
                logger.error("Invalid device data and no station_id provided")
                return []

        if not start_date or not end_date:
            logger.error("Start date and end date must be provided")
            return []

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone('UTC'))
            end = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone('UTC'))
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            return []

        stations = self.get_all_stations(user_id)
        station = next((s for s in stations if s["station_id"] == station_id), None) if station_id else None
        time_zone = station["time_zone"] if station else 5.5

        historical_data = []
        current_date = start
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            page_no = 1
            page_size = 100

            while True:
                params = {
                    "id": device["id"],
                    "sn": device["sn"],
                    "time": date_str,
                    "timeZone": time_zone,
                    "pageNo": page_no,
                    "pageSize": page_size
                }
                response = self.make_request("POST", "inverterDay", params)
                if not response:
                    logger.warning(f"No data for device {device['sn']} on {date_str}, page {page_no}")
                    break

                data = response.get("data", {})
                records = data.get("page", {}).get("records", [])
                if not isinstance(records, list):
                    logger.error(f"Invalid records format for device {device['sn']} on {date_str}: {records}")
                    break

                for record in records:
                    if not isinstance(record, dict):
                        logger.error(f"Invalid record for device {device['sn']} on {date_str}: {record}")
                        continue
                    timestamp_ms = int(record.get("dataTimestamp", 0))
                    if not timestamp_ms:
                        logger.warning(f"Missing dataTimestamp for record on {date_str}: {record}")
                        continue
                    timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone('UTC'))
                    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                    entry = {
                        "timestamp": timestamp_str,
                        "total_power": float(record.get("pac", 0.0)),
                        "energy_today": float(record.get("eToday", 0.0)),
                        "pr": float(record.get("pr", 0.0)),
                        "state": str(record.get("state", "unknown")),
                        "r_voltage": float(record.get("uAc1", 0.0)),
                        "s_voltage": float(record.get("uAc2", 0.0)),
                        "t_voltage": float(record.get("uAc3", 0.0)),
                        "r_current": float(record.get("iAc1", 0.0)),
                        "s_current": float(record.get("iAc2", 0.0)),
                        "t_current": float(record.get("iAc3", 0.0)),
                    }
                    for i in range(1, 13):
                        entry[f"pv{i:02d}_voltage"] = float(record.get(f"uPv{i}", 0.0))
                        entry[f"pv{i:02d}_current"] = float(record.get(f"iPv{i}", 0.0))
                    historical_data.append(entry)

                total_records = data.get("page", {}).get("total", 0)
                logger.info(f"Fetched {len(records)} records for device {device['sn']} on {date_str}, page {page_no}. Total: {total_records}")
                if page_no * page_size >= total_records:
                    break
                page_no += 1

            current_date += timedelta(days=1)

        logger.info(f"Total historical data entries for device {device['sn']}: {len(historical_data)}")
        return historical_data
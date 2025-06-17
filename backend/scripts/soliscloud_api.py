import requests
import hmac
import hashlib
import time
import json
import logging
import os
import base64
import sys
import csv
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from io import TextIOWrapper
from typing import Any, List, Dict, Optional
from pytz import timezone

# Ensure logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'soliscloud_api.log')

# Create a stream handler with UTF-8 encoding
stream_handler = logging.StreamHandler(stream=TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5),
        stream_handler
    ]
)
logger = logging.getLogger(__name__)

class SolisCloudAPI:
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://www.soliscloud.com:13333"):
        self.api_key = api_key.strip()
        self.api_secret = api_secret.strip()
        self.base_url = base_url
        self.rate_limit_delay = 0.6  # Fixed delay as in working code

    def generate_signature(self, method, path, content_md5, content_type, date):
        canonical_content_type = content_type.split(';')[0]
        canonical_string = f"{method}\n{content_md5}\n{canonical_content_type}\n{date}\n{path}"
        logger.debug(f"Canonical string for signature: {canonical_string}")
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            canonical_string.encode('utf-8'),
            hashlib.sha1
        ).digest()
        return base64.b64encode(signature).decode('utf-8')

    def make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Optional[Dict]:
        max_retries = 3
        retry_delay = 1

        endpoint = endpoint.lstrip("/")
        path = f"/v1/api/{endpoint}"
        content_type = "application/json;charset=UTF-8"

        for attempt in range(max_retries):
            timestamp = str(int(time.time()))
            date_header = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
            payload_str = json.dumps(payload or {}, separators=(',', ':'))
            md5_hash = hashlib.md5(payload_str.encode('utf-8')).digest()
            content_md5 = base64.b64encode(md5_hash).decode('utf-8')

            signature = self.generate_signature(method, path, content_md5, content_type, date_header)

            headers = {
                "Content-Type": content_type,
                "Authorization": f"API {self.api_key}:{signature}",
                "Timestamp": timestamp,
                "Date": date_header,
                "Content-MD5": content_md5
            }

            url = f"{self.base_url}{path}"
            safe_headers = {k: ("***" if k == "Authorization" else v) for k, v in headers.items()}
            logger.debug(f"Attempt {attempt + 1}/{max_retries}: Making {method} request to {url} with headers: {safe_headers} and payload: {payload}")

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                logger.debug(f"Response from {endpoint}: {data}")

                if not data.get("success") or data.get("code") != "0":
                    error_msg = data.get("msg", "Unknown error")
                    error_code = data.get("code", "Unknown")
                    logger.error(f"API error for {endpoint}: {error_msg} (code: {error_code})")
                    if error_code in ["R0000", "403"]:
                        logger.error(f"Permission denied for {path}. Check API key permissions.")
                        return None
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying after {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    return None

                time.sleep(self.rate_limit_delay)  # Fixed delay
                return data
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed for /{endpoint}: {e}")
                if 'response' in locals():
                    logger.error(f"Response: {response.text}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying after {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                logger.error(f"Failed to complete request after {max_retries} attempts.")
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
                    create_date = datetime.fromtimestamp(create_date / 1000).strftime('%Y-%m-%d')
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

    def get_inverter_real_time_data(self, user_id: str, username: str = None, password: str = None, device: Dict[str, Any] = None) -> Dict[str, Any]:
        if not device or not device.get("id") or not device.get("sn"):
            logger.error("Invalid device data provided")
            return {}

        params = {"id": device["id"], "sn": device["sn"]}
        response = self.make_request("POST", "inverterDetail", params)
        if not response:
            logger.warning(f"No real-time data for device {device['sn']}")
            return {}

        data = response.get("data", {})
        if not isinstance(data, dict):
            logger.error(f"Unexpected data format for device {device['sn']}: {data}")
            return {}

        timestamp_ms = int(data.get("dataTimestamp", 0))
        entry = {
            "timestamp": datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S') if timestamp_ms else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
        return entry

    def get_inverter_historical_data(self, user_id: str, username: str = None, password: str = None, device: Dict[str, Any] = None, start_date: str = None, end_date: str = None, station_id: str = None, csv_file: str = "soliscloud_inverter_data.csv") -> List[Dict[str, Any]]:
        if not device or not device.get("id") or not device.get("sn"):
            # Auto-fetch inverter if station_id is provided
            if station_id:
                inverters = self.get_all_inverters(user_id, station_id=station_id)
                if inverters:
                    device = inverters[0]  # Take first inverter
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
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            return []

        # Get station details for time_zone and name
        stations = self.get_all_stations(user_id)
        station = next((s for s in stations if s["station_id"] == station_id), None) if station_id else None
        station_name = station["plant_name"] if station else "Unknown"
        time_zone = station["time_zone"] if station else 5.5

        # Initialize CSV
        historical_data = []
        csv_initialized = False
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            headers = [
                "Station ID", "Station Name", "Inverter ID", "Inverter SN", "Power (kW)",
                "Daily Energy (kWh)", "Time", "Time String",
                "iPv1", "iPv2", "iPv3", "iPv4", "iPv5", "iPv6",
                "uPv1", "uPv2", "uPv3", "uPv4", "uPv5", "uPv6",
                "r_voltage", "s_voltage", "t_voltage", "r_current", "s_current", "t_current"
            ]
            writer.writerow(headers)
            csv_initialized = True
            logger.debug(f"Wrote CSV headers: {headers}")

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
                    # Try data.page.records first (per API docs), fallback to data as list
                    records = data.get("page", {}).get("records", []) if isinstance(data, dict) else data
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
                        try:
                            timestamp = datetime.fromtimestamp(timestamp_ms / 1000, timezone('UTC')).astimezone(timezone('Asia/Kolkata'))
                            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        except (ValueError, TypeError) as e:
                            logger.error(f"Invalid timestamp {timestamp_ms} for record on {date_str}: {e}")
                            timestamp_str = record.get("timeStr", "")

                        record_tz = record.get("timeZone", time_zone)
                        if record_tz != time_zone:
                            logger.warning(f"Time zone mismatch for {date_str}: expected {time_zone}, got {record_tz}")

                        entry = {
                            "timestamp": timestamp_str,
                            "total_power": float(record.get("pac", 0.0)),
                            "energy_today": float(record.get("eToday", 0.0)),
                            "pr": float(record.get("pr", 0.0)),
                            "state": str(record.get("state", "unknown")),
                            "station_id": station_id or "",
                            "station_name": station_name,
                            "inverter_id": device["id"],
                            "inverter_sn": device["sn"]
                        }
                        for i in range(1, 7):
                            entry[f"pv{i:02d}_current"] = float(record.get(f"iPv{i}", 0.0))
                            entry[f"pv{i:02d}_voltage"] = float(record.get(f"uPv{i}", 0.0))
                        for phase in ["r", "s", "t"]:
                            phase_idx = {"r": 1, "s": 2, "t": 3}[phase]
                            entry[f"{phase}_voltage"] = float(record.get(f"uAc{phase_idx}", 0.0))
                            entry[f"{phase}_current"] = float(record.get(f"iAc{phase_idx}", 0.0))

                        # Write to CSV
                        row = [
                            entry["station_id"],
                            entry["station_name"],
                            entry["inverter_id"],
                            entry["inverter_sn"],
                            entry["total_power"],
                            entry["energy_today"],
                            record.get("dataTimestamp", ""),
                            entry["timestamp"],
                            *[entry[f"pv{i:02d}_current"] for i in range(1, 7)],
                            *[entry[f"pv{i:02d}_voltage"] for i in range(1, 7)],
                            entry["r_voltage"],
                            entry["s_voltage"],
                            entry["t_voltage"],
                            entry["r_current"],
                            entry["s_current"],
                            entry["t_current"]
                        ]
                        writer.writerow(row)
                        logger.debug(f"Wrote CSV row for {date_str}: {row}")

                        historical_data.append(entry)

                    total_records = data.get("page", {}).get("total", 0) if isinstance(data, dict) else len(records)
                    logger.info(f"Fetched {len(records)} records for device {device['sn']} on {date_str}, page {page_no}. Total: {total_records}")
                    if page_no * page_size >= total_records:
                        break
                    page_no += 1

                # Validate 5-minute intervals
                day_records = [r for r in historical_data if r["timestamp"].startswith(date_str)]
                if day_records:
                    timestamps = [datetime.strptime(r["timestamp"], '%Y-%m-%d %H:%M:%S') for r in day_records]
                    for i in range(1, len(timestamps)):
                        interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                        if abs(interval - 300) > 1:  # 300s = 5 minutes
                            logger.warning(f"Irregular interval on {date_str}: {interval}s between {timestamps[i-1]} and {timestamps[i]}")

                current_date += timedelta(days=1)

        if csv_initialized:
            logger.info(f"Data written to {csv_file}")
        logger.info(f"Total historical data entries for device {device['sn']}: {len(historical_data)}")
        return historical_data
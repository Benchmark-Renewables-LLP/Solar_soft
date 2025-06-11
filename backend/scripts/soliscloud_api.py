import requests
import hmac
import hashlib
import time
import json
import logging
import os
import re
from datetime import datetime
import pytz

# Ensure logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'soliscloud_api.log')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SolisCloudAPI:
    def __init__(self, api_key, api_secret, base_url="https://www.soliscloud.com:13333"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.rate_limit_delay = 1
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def generate_signature(self, path, timestamp, payload):
        payload_str = json.dumps(payload) if payload else ""
        message = f"{path}{timestamp}{payload_str}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha1
        ).hexdigest()
        return signature

    def handle_rate_limit(self, response):
        remaining = response.headers.get('X-Rate-Limit-Remaining')
        reset = response.headers.get('X-Rate-Limit-Reset')
        if remaining:
            self.rate_limit_remaining = int(remaining)
        if reset:
            self.rate_limit_reset = int(reset)
        if self.rate_limit_remaining is not None and self.rate_limit_remaining <= 1:
            reset_time = self.rate_limit_reset or (int(time.time()) + 60)
            wait_time = max(reset_time - int(time.time()), 1)
            logger.warning(f"Rate limit nearly reached. Waiting {wait_time} seconds.")
            time.sleep(wait_time)
        else:
            time.sleep(self.rate_limit_delay)

    def make_request(self, method, endpoint, payload=None):
        timestamp = str(int(time.time()))
        path = f"/v1/api{endpoint}"
        signature = self.generate_signature(path, timestamp, payload)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"API {self.api_key}:{signature}",
            "Timestamp": timestamp
        }

        url = f"{self.base_url}{path}"
        logger.info(f"Making {method} request to {url} with payload: {payload}")
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=payload, timeout=10)
            else:
                response = requests.get(url, headers=headers, params=payload, timeout=10)
            response.raise_for_status()
            self.handle_rate_limit(response)
            data = response.json()
            logger.debug(f"Response from {url}: {data}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            if 'response' in locals():
                logger.error(f"Response: {response.text}")
            return None

    def fetch_station_list(self, user_id, username=None, password=None):
        endpoint = "/userStationList"
        all_stations = []
        page = 1
        page_size = 100

        while True:
            payload = {
                "userId": user_id,
                "pageNo": page,
                "pageSize": page_size
            }
            response = self.make_request("POST", endpoint, payload)
            if not response or not response.get("success"):
                logger.warning(f"No stations found for user {user_id} on page {page}")
                break

            data = response.get("data", {})
            stations = data.get("stationList", [])
            all_stations.extend(stations)

            total_pages = data.get("totalPages", 1)
            logger.info(f"Fetched {len(stations)} stations for user {user_id} on page {page}/{total_pages}")
            if page >= total_pages:
                break
            page += 1

        logger.info(f"Fetched a total of {len(all_stations)} stations for user {user_id}")
        return all_stations

    def fetch_station_inverters(self, user_id, username=None, password=None, station_id=None):
        endpoint = "/inverterList"
        payload = {"stationId": station_id}
        response = self.make_request("POST", endpoint, payload)
        if response and response.get("success"):
            inverters = response.get("data", {}).get("inverterList", [])
            logger.info(f"Fetched {len(inverters)} inverters for station {station_id}")
            return inverters
        logger.warning(f"No inverters found for station {station_id}")
        return []

    def fetch_inverter_detail(self, user_id, username=None, password=None, device=None):
        endpoint = "/inverterDetail"
        payload = {
            "inverterId": device["id"],
            "inverterSn": device["sn"]
        }
        response = self.make_request("POST", endpoint, payload)
        if response and response.get("success"):
            detail_data = response.get("data", {})
            logger.info(f"Fetched real-time data for device {device['sn']}")
            return self.process_inverter_detail(device, detail_data)
        logger.warning(f"No real-time data for device {device['sn']}")
        return []

    def process_inverter_detail(self, device, detail_data):
        with open('field_mappings.json', 'r') as f:
            mappings = json.load(f)
        field_mapping = mappings.get('soliscloud', {})

        entry = {
            "device_id": device["sn"],
            "station_id": device.get("stationId"),
            "station_name": device.get("stationName")
        }

        # Handle timestamp and convert to IST
        ts_str = detail_data.get("dataTimestamp")
        if not ts_str:
            logger.warning(f"Missing timestamp in record: {detail_data}")
            entry["timestamp"] = None
        else:
            try:
                if isinstance(ts_str, (int, float)):
                    ts = datetime.fromtimestamp(ts_str / 1000, tz=pytz.UTC)
                else:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                ist = ts.astimezone(pytz.timezone("Asia/Kolkata"))
                entry["timestamp"] = ist.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                logger.warning(f"Error parsing timestamp {ts_str}: {e}")
                entry["timestamp"] = None

        # Apply field mappings, including regex-based mappings
        for api_field, db_field in field_mapping.items():
            if api_field.startswith("uPv") or api_field.startswith("iPv"):
                # Handle regex mappings for PV fields
                for key in detail_data.keys():
                    match = re.match(api_field, key)
                    if match:
                        pv_num = int(match.group(1))
                        if pv_num > 12:  # Filter out PV inputs beyond 12
                            continue
                        mapped_field = db_field % pv_num  # e.g., pv%02d_voltage → pv01_voltage
                        value = detail_data.get(key)
                        try:
                            entry[mapped_field] = float(value) if value is not None else None
                        except (ValueError, TypeError):
                            entry[mapped_field] = None
            else:
                # Direct mapping
                value = detail_data.get(api_field)
                try:
                    entry[db_field] = float(value) if value is not None else None
                except (ValueError, TypeError):
                    entry[db_field] = None

        # Initialize all expected database fields, setting unmapped ones to None
        for i in range(1, 13):
            pv_voltage = f"pv{i:02d}_voltage"
            pv_current = f"pv{i:02d}_current"
            if pv_voltage not in entry:
                entry[pv_voltage] = None
            if pv_current not in entry:
                entry[pv_current] = None

        for field in ["r_voltage", "s_voltage", "t_voltage", "r_current", "s_current", "t_current",
                      "total_power", "energy_today", "pr", "state"]:
            if field not in entry:
                entry[field] = None

        return [entry]  # Return as a list for consistency with other methods

def main():
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    solis_api = SolisCloudAPI(api_key, api_secret)

    user_id = "your_user_id"
    stations = solis_api.fetch_station_list(user_id)
    if not stations:
        logger.error("No stations found, exiting.")
        return

    station = stations[0]
    inverters = solis_api.fetch_station_inverters(user_id, station_id=station["id"])
    if not inverters:
        logger.error(f"No inverters found for station {station['id']}, exiting.")
        return

    inverter = inverters[0]
    detail_data = solis_api.fetch_inverter_detail(user_id, device=inverter)
    logger.info(f"Processed {len(detail_data)} real-time data entries for inverter {inverter['sn']}")

if __name__ == "__main__":
    main()
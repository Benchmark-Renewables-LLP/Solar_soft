import requests
import hmac
import hashlib
import time
import json
import logging
import os
import base64
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Any
from time import strftime, gmtime

# Ensure logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'soliscloud_api.log')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SolisCloudAPI:
    def __init__(self, api_key, api_secret, base_url="https://www.soliscloud.com:13333"):
        self.api_key = api_key.strip()
        self.api_secret = api_secret.strip()
        self.base_url = base_url
        self.rate_limit_delay = 2
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def _get_gmt_time(self):
        try:
            return strftime("%a, %-d %b %Y %H:%M:%S GMT", gmtime())
        except ValueError:
            return strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime()).replace(" 0", " ")

    def _get_content_md5(self, payload):
        payload_str = json.dumps(payload or {}, separators=(',', ':'), ensure_ascii=False)
        md5_hash = hashlib.md5(payload_str.encode('utf-8')).digest()
        return base64.b64encode(md5_hash).decode('utf-8'), payload_str

    def generate_signature(self, method, path, content_md5, content_type, date):
        canonical_string = f"{method}\n{content_md5}\n{content_type}\n{date}\n{path}"
        logger.debug("\nSIGNATURE DEBUG >>>")
        logger.debug("Method: %s", method)
        logger.debug("Path: %s", path)
        logger.debug("Content-MD5: %s", content_md5)
        logger.debug("Content-Type: %s", content_type)
        logger.debug("Date: %s", date)
        logger.debug("Canonical String:\n%s", canonical_string)

        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            canonical_string.encode('utf-8'),
            hashlib.sha1
        ).digest()
        encoded = base64.b64encode(signature).decode('utf-8')
        logger.debug("Generated Signature: %s", encoded)
        logger.debug("Authorization Header: API %s:%s", self.api_key, encoded)
        logger.debug("<<< END SIGNATURE DEBUG")
        return encoded

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
            time.sleep(self.rate_limit_delay or 2)

    def make_request(self, method, endpoint, payload=None):
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            timestamp = str(int(time.time()))
            date_header = self._get_gmt_time()
            endpoint = endpoint.lstrip("/")
            path = f"/v1/api/{endpoint}"
            content_type = "application/json;charset=UTF-8"

            content_md5, payload_str = self._get_content_md5(payload)
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
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Making {method} request to {url} with headers: {safe_headers} and payload: {payload}")

            try:
                if method == "POST":
                    response = requests.post(url, headers=headers, json=payload, timeout=30)
                else:
                    response = requests.get(url, headers=headers, params=payload, timeout=30)
                response.raise_for_status()
                self.handle_rate_limit(response)
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed for /{endpoint}: {e}")
                if 'response' in locals():
                    logger.error(f"Response: {response.text}")
                    if response.status_code == 408 and attempt < max_retries - 1:
                        logger.info(f"Retrying after {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                return None

        logger.error(f"Failed to complete request after {max_retries} attempts.")
        return None

    def get_all_stations(self):
        stations = []
        page = 1
        while True:
            payload = {"pageNo": page, "pageSize": 100}
            response = self.make_request("POST", "userStationList", payload)
            if not response or not response.get("success"):
                break
            station_list = response.get("data", {}).get("stationList", [])
            stations.extend(station_list)
            if page >= response.get("data", {}).get("totalPages", 1):
                break
            page += 1
        return stations

    def get_inverters_by_station(self, station_id):
        inverters = []
        page = 1
        while True:
            payload = {"stationId": station_id, "pageNo": page, "pageSize": 100}
            response = self.make_request("POST", "inverterList", payload)
            if not response or not response.get("success"):
                break
            inverter_list = response.get("data", {}).get("inverterList", [])
            inverters.extend(inverter_list)
            if page >= response.get("data", {}).get("totalPages", 1):
                break
            page += 1
        return inverters

if __name__ == "__main__":
    # Replace these values directly in the script
 
    api_key = "1300386381677745367"  # Replace with your API ID
    api_secret = "ba3f0b1cfdd64680b2bf91c13379b33a"

    client = SolisCloudAPI(api_key, api_secret)
    stations = client.get_all_stations()

    if stations:
        print(f"\n✅ SUCCESS: Found {len(stations)} station(s).\n")
        for s in stations:
            print(f"Station: {s.get('stationName')} | ID: {s.get('id')}")
            inverters = client.get_inverters_by_station(s.get('id'))
            if inverters:
                for inv in inverters:
                    print(f"  - Inverter SN: {inv.get('sn')} | ID: {inv.get('id')}")
            else:
                print("  - No inverters found")
    else:
        print("\n❌ FAILED: Could not fetch stations. Invalid API key/secret or no data.")
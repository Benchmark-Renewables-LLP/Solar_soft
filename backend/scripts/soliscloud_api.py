import requests
import hmac
import hashlib
import time
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SolisCloudAPI:
    def __init__(self, api_key, api_secret, base_url="https://www.soliscloud.com:13333"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url

    def generate_signature(self, path, timestamp, payload):
        """Generate HMAC-SHA1 signature for SolisCloud API request."""
        payload_str = json.dumps(payload) if payload else ""
        message = f"{path}{timestamp}{payload_str}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha1
        ).hexdigest()
        return signature

    def make_request(self, method, endpoint, payload=None):
        """Make an API request with authentication."""
        timestamp = str(int(time.time()))
        path = f"/v1/api{endpoint}"
        signature = self.generate_signature(path, timestamp, payload)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"API {self.api_key}:{signature}",
            "Timestamp": timestamp
        }

        url = f"{self.base_url}{path}"
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=payload, timeout=10)
            else:
                response = requests.get(url, headers=headers, params=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            if response:
                logger.error(f"Response: {response.text}")
            return None

    def fetch_station_list(self, user_id):
        """Fetch list of stations (plants) for a user."""
        endpoint = "/userStationList"
        payload = {"userId": user_id}
        response = self.make_request("POST", endpoint, payload)
        if response and response.get("success"):
            return response.get("data", {}).get("stationList", [])
        logger.warning(f"No stations found for user {user_id}")
        return []

    def fetch_station_inverters(self, station_id):
        """Fetch list of inverters for a station."""
        endpoint = "/inverterList"
        payload = {"stationId": station_id}
        response = self.make_request("POST", endpoint, payload)
        if response and response.get("success"):
            return response.get("data", {}).get("inverterList", [])
        logger.warning(f"No inverters found for station {station_id}")
        return []

    def fetch_historical_data(self, device, start_date, end_date):
        """Fetch historical data for a device (inverter) over a date range."""
        endpoint = "/inverterDay"
        payload = {
            "inverterId": device["id"],
            "inverterSn": device["sn"],
            "startDate": start_date,  # Format: YYYY-MM-DD
            "endDate": end_date      # Format: YYYY-MM-DD
        }
        response = self.make_request("POST", endpoint, payload)
        if response and response.get("success"):
            daily_data = response.get("data", {}).get("dailyData", [])
            return self.process_historical_data(device, daily_data)
        logger.warning(f"No historical data for device {device['sn']}")
        return []

    def process_historical_data(self, device, daily_data):
        """Process historical data into a standardized format."""
        processed_data = []
        field_mapping = {
            "pv1Voltage": "pv01_voltage",
            "pv1Current": "pv01_current",
            "pv2Voltage": "pv02_voltage",
            "pv2Current": "pv02_current",
            # Add mappings for pv3 to pv12 as needed
            "gridVoltage": "r_voltage",  # Assuming single-phase for simplicity
            "gridCurrent": "r_current",
            "power": "total_power",
            "energyDay": "energy_today",
            "performanceRatio": "pr"
        }

        for record in daily_data:
            entry = {"device_id": device["sn"]}
            # Extract timestamp
            ts_str = record.get("time")  # Expected format: YYYY-MM-DD HH:MM:SS
            if not ts_str:
                logger.warning(f"Missing timestamp in record: {record}")
                continue
            entry["timestamp"] = ts_str

            # Map fields to standardized keys
            for api_field, db_field in field_mapping.items():
                value = record.get(api_field)
                entry[db_field] = float(value) if value is not None else None

            # Set unused fields to None for consistency
            for i in range(1, 13):
                pv_voltage = f"pv{i:02d}_voltage"
                pv_current = f"pv{i:02d}_current"
                if pv_voltage not in entry:
                    entry[pv_voltage] = None
                if pv_current not in entry:
                    entry[pv_current] = None

            # Set other fields to None if not present
            for field in ["s_voltage", "t_voltage", "s_current", "t_current", "state"]:
                if field not in entry:
                    entry[field] = None

            processed_data.append(entry)

        return processed_data

def main():
    # Example usage
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    solis_api = SolisCloudAPI(api_key, api_secret)

    # Fetch stations for a user
    user_id = "your_user_id"
    stations = solis_api.fetch_station_list(user_id)
    if not stations:
        logger.error("No stations found, exiting.")
        return

    # Fetch inverters for the first station
    station = stations[0]
    inverters = solis_api.fetch_station_inverters(station["id"])
    if not inverters:
        logger.error(f"No inverters found for station {station['id']}, exiting.")
        return

    # Fetch historical data for the first inverter
    inverter = inverters[0]
    start_date = "2025-06-08"
    end_date = "2025-06-09"
    historical_data = solis_api.fetch_historical_data(inverter, start_date, end_date)
    logger.info(f"Fetched {len(historical_data)} historical data entries for inverter {inverter['sn']}")

if __name__ == "__main__":
    main()
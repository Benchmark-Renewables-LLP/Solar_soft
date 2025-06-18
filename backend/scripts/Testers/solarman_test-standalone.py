import json
import logging
import time
import csv
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from dateutil import tz

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def json_to_csv(json_data: Dict) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["collectTime", "deviceSn", "deviceType", "name", "value", "unit", "key"],
        lineterminator='\n'
    )
    writer.writeheader()

    device_sn = json_data.get("deviceSn", "")
    device_type = json_data.get("deviceType", "")

    # Handle historical data (paramDataList)
    param_data_list = json_data.get("paramDataList", [])
    if param_data_list:
        for param_data in param_data_list:
            collect_time_raw = param_data.get("collectTime", "")
            if isinstance(collect_time_raw, str):
                collect_time = collect_time_raw
            else:
                collect_time = datetime.utcfromtimestamp(int(collect_time_raw)).strftime('%Y-%m-%d %H:%M:%S')
            data_list = param_data.get("dataList", [])

            for item in data_list:
                row = {
                    "collectTime": collect_time,
                    "deviceSn": device_sn,
                    "deviceType": device_type,
                    "name": item.get("name", ""),
                    "value": item.get("value", ""),
                    "unit": item.get("unit", ""),
                    "key": item.get("key", "")
                }
                writer.writerow(row)
    # Handle real-time data (dataList)
    else:
        data_list = json_data.get("dataList", [])
        collect_time = datetime.now(tz.tzutc()).strftime('%Y-%m-%d %H:%M:%S')
        for item in data_list:
            row = {
                "collectTime": collect_time,
                "deviceSn": device_sn,
                "deviceType": device_type,
                "name": item.get("name", ""),
                "value": item.get("value", ""),
                "unit": item.get("unit", ""),
                "key": item.get("key", "")
            }
            writer.writerow(row)

    csv_content = output.getvalue()
    output.close()
    return csv_content

def json_to_name_columns_csv(json_data: Dict) -> str:
    output = io.StringIO()
    data_list = json_data.get("dataList", [])
    
    # Create headers from 'name' fields
    fieldnames = [item.get("name", "") for item in data_list]
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        lineterminator='\n',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()

    # Create single row from 'value' fields
    row = {item.get("name", ""): item.get("value", "") for item in data_list}
    writer.writerow(row)

    csv_content = output.getvalue()
    output.close()
    return csv_content

class SolarmanAPI:
    def __init__(self, email: str, password_sha256: str, app_id: str, app_secret: str):
        self.base_url = "https://globalapi.solarmanpv.com"
        self.email = email
        self.password_sha256 = password_sha256
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[float] = None

    def _is_token_expired(self) -> bool:
        if not self.access_token or not self.token_expiry:
            return True
        return time.time() >= self.token_expiry

    def get_access_token(self) -> None:
        url = f"{self.base_url}/account/v1.0/token?appId={self.app_id}"
        payload = {
            "appSecret": self.app_secret,
            "email": self.email,
            "password": self.password_sha256,
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Token response: {json.dumps(data, indent=2, ensure_ascii=False)}")

            if data.get("success"):
                self.access_token = data["access_token"]
                expires_in_str = data.get("expires_in")
                if expires_in_str is None:
                    logger.error("expires_in not found in token response")
                    raise Exception("expires_in not found in token response")
                try:
                    expires_in = int(expires_in_str)
                except ValueError as e:
                    logger.error(f"Invalid expires_in value: {expires_in_str}")
                    raise Exception(f"Invalid expires_in value: {expires_in_str}")
                self.token_expiry = time.time() + expires_in - 300
                logger.info("Access token obtained successfully")
            else:
                logger.error(f"Failed to obtain access token: {data.get('msg')}")
                raise Exception("Failed to obtain access token")
        except requests.RequestException as e:
            logger.error(f"Error obtaining access token: {str(e)}")
            raise

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict:
        if self._is_token_expired():
            logger.info("Access token expired or not set. Obtaining new token...")
            self.get_access_token()

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, params=params, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            result = response.json()
            logger.debug(f"API response: {json.dumps(result, indent=2, ensure_ascii=False)}")

            if not result.get("success"):
                logger.error(f"API request failed: {result.get('msg')}")
                raise Exception(f"API request failed: {result.get('msg')}")
            return result

        except requests.RequestException as e:
            logger.error(f"Error making API request: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise

    def get_plant_list(self) -> List[Dict]:
        endpoint = "/station/v1.0/list?language=en"
        try:
            response = self._make_request("POST", endpoint, data={})
            return response.get("stationList", [])
        except Exception as e:
            logger.error(f"Error fetching plant list: {str(e)}")
            raise

    def get_all_devices(self, plant_id: int, device_type: Optional[str] = None) -> List[Dict]:
        endpoint = "/station/v1.0/device?language=en"
        payload = {"stationId": plant_id}
        if device_type:
            payload["deviceType"] = device_type
        try:
            response = self._make_request("POST", endpoint, data=payload)
            devices = response.get("deviceListItems") or response.get("deviceList", [])
            return devices
        except Exception as e:
            logger.error(f"Error fetching devices for plant {plant_id}: {str(e)}")
            raise

    def get_historical_data(
        self,
        device: Dict,
        start_date: str,
        end_date: str,
        time_type: int = 1
    ) -> Dict:
        endpoint = "/device/v1.0/historical?language=en"
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            logger.error(f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
            raise

        utc = tz.tzutc()
        now = datetime.now(utc)
        start_dt = start_dt.replace(tzinfo=utc)
        end_dt = end_dt.replace(hour=23, minute=59, second=59, tzinfo=utc)

        if end_dt > now:
            end_dt = now
        if start_dt >= end_dt:
            raise ValueError("start_date must be before end_date")

        payload = {
            "deviceSn": device.get("deviceSn", ""),
            "deviceType": device.get("deviceType", "INVERTER"),
            "startTime": start_dt.strftime('%Y-%m-%d'),
            "endTime": end_dt.strftime('%Y-%m-%d'),
            "timeType": time_type
        }
        logger.debug(f"Requesting historical data with payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        try:
            response = self._make_request("POST", endpoint, data=payload)
            return response
        except Exception as e:
            logger.error(f"Error fetching historical data for device {device.get('deviceSn', 'unknown')}: {str(e)}")
            raise

    def get_current_data(
        self,
        device: Dict,
        language: str = "en"
    ) -> Dict:
        endpoint = "/device/v1.0/currentData"
        params = {"language": language}
        payload = {
            "deviceSn": device.get("deviceSn", ""),
        }
        if "deviceId" in device and device["deviceId"]:
            payload["deviceId"] = device["deviceId"]

        logger.debug(f"Requesting current data with payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        try:
            response = self._make_request("POST", endpoint, params=params, data=payload)
            return response
        except Exception as e:
            logger.error(f"Error fetching current data for device {device.get('deviceSn', 'unknown')}: {str(e)}")
            raise

def main(start_date: str = None, end_date: str = None):
    # Hardcoded credentials
    email = "Maintenanceunit2@gspcrop.in"
    password_sha256 = "ff2612c35745d5bbdf4103f986c7279f31ff7b728da17469256ffa019f59aa9c"
    app_id = "3124071788531342"
    app_secret = "95bdc99830b61580123a96dad4bb7bc7"

    # Default to broader date range for testing
    if not start_date or not end_date:
        end_dt = datetime.now(tz.tzutc())
        start_dt = end_dt - timedelta(days=30)  # Approx one month
        start_date = start_dt.strftime('%Y-%m-%d')
        end_date = end_dt.strftime('%Y-%m-%d')

    # Initialize API client
    api = SolarmanAPI(email, password_sha256, app_id, app_secret)

    try:
        # Step 1: Get all plants
        plants = api.get_plant_list()
        if not plants:
            logger.info("No plants found.")
            return

        # Step 2: Iterate through each plant and fetch devices
        for plant in plants:
            plant_id = plant.get("id", "Unknown ID")
            plant_name = plant.get("name", "Unknown Station")
            logger.info(f"Fetching devices for plant: {plant_name} (ID: {plant_id})")

            devices = api.get_all_devices(plant_id)
            logger.info(f"Devices for plant {plant_name}: {json.dumps(devices, indent=2, ensure_ascii=False)}")
            if not devices:
                logger.info(f"No devices found for plant: {plant_name}")
                continue

            # Step 3: Fetch data for each device
            for device in devices:
                device_sn = device.get("deviceSn", "unknown")
                device["plant_id"] = plant_id
                if device.get("connectStatus") == 0:
                    logger.info(f"Skipping disconnected device: {device_sn}")
                    continue
                logger.info(f"Processing device: {device_sn}")

                try:
                    # Fetch historical data (timeType 2 for daily data)
                    historical_data = api.get_historical_data(device, start_date, end_date, time_type=2)
                    logger.info(f"Historical data for device {device_sn}: {json.dumps(historical_data, indent=2, ensure_ascii=False)}")
                    if historical_data.get("paramDataList"):
                        csv_data = json_to_csv(historical_data)
                        csv_filename = f"historical_data_{device_sn}.csv"
                        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                            f.write(csv_data)
                        logger.info(f"Saved historical data to {csv_filename}")
                    else:
                        logger.info(f"No historical data available for device {device_sn}")
                except Exception as e:
                    logger.error(f"Failed to fetch historical data for device {device_sn}: {str(e)}")

                try:
                    # Fetch real-time data
                    current_data = api.get_current_data(device)
                    logger.info(f"Current data for device {device_sn}: {json.dumps(current_data, indent=2, ensure_ascii=False)}")
                    if current_data.get("dataList"):
                        # Save standard CSV
                        csv_data = json_to_csv(current_data)
                        csv_filename = f"current_data_{device_sn}.csv"
                        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                            f.write(csv_data)
                        logger.info(f"Saved current data to {csv_filename}")
                        # Save name-as-columns CSV
                        name_columns_csv_data = json_to_name_columns_csv(current_data)
                        name_columns_csv_filename = f"current_data_name_columns_{device_sn}.csv"
                        with open(name_columns_csv_filename, 'w', newline='', encoding='utf-8') as f:
                            f.write(name_columns_csv_data)
                        logger.info(f"Saved name-as-columns current data to {name_columns_csv_filename}")
                    else:
                        logger.info(f"No current data available for device {device_sn}")
                except Exception as e:
                    logger.error(f"Failed to fetch current data for device {device_sn}: {str(e)}")

    except Exception as e:
        logger.error(f"An error occurred in main: {str(e)}")

if __name__ == "__main__":
    main()
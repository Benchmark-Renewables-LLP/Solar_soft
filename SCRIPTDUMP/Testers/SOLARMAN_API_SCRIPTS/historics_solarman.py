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
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def json_to_name_columns_csv(json_data: Dict) -> str:
    output = io.StringIO()
    param_data_list = json_data.get("paramDataList", [])
    
    if not param_data_list or not param_data_list[0].get("dataList"):
        return ""
    
    fieldnames = ["collectTime"] + [item.get("name", "") for item in param_data_list[0].get("dataList", [])]
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        lineterminator='\n',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()

    for param_data in param_data_list:
        collect_time_raw = param_data.get("collectTime", "")
        collect_time = (
            collect_time_raw if isinstance(collect_time_raw, str)
            else datetime.utcfromtimestamp(int(collect_time_raw)).strftime('%Y-%m-%d %H:%M:%S')
        )
        row = {"collectTime": collect_time}
        for item in param_data.get("dataList", []):
            row[item.get("name", "")] = item.get("value", "")
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
        return not self.access_token or not self.token_expiry or time.time() >= self.token_expiry

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
                expires_in = int(data.get("expires_in", 0))
                if expires_in == 0:
                    raise Exception("expires_in not found or invalid")
                self.token_expiry = time.time() + expires_in - 300
                logger.info("Access token obtained successfully")
            else:
                raise Exception(f"Failed to obtain access token: {data.get('msg')}")
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
            self.get_access_token()

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        try:
            response = (
                requests.get(url, headers=headers, params=params, timeout=10) if method.upper() == "GET"
                else requests.post(url, headers=headers, params=params, json=data, timeout=10)
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"API response: {json.dumps(result, indent=2, ensure_ascii=False)}")

            if not result.get("success"):
                raise Exception(f"API request failed: {result.get('msg')}")
            return result
        except requests.RequestException as e:
            logger.error(f"Error making API request: {str(e)}")
            raise

    def get_plant_list(self) -> List[Dict]:
        endpoint = "/station/v1.0/list?language=en"
        try:
            return self._make_request("POST", endpoint, data={}).get("stationList", [])
        except Exception as e:
            logger.error(f"Error fetching plant list: {str(e)}")
            raise

    def get_all_devices(self, plant_id: int) -> List[Dict]:
        endpoint = "/station/v1.0/device?language=en"
        payload = {"stationId": plant_id}
        try:
            response = self._make_request("POST", endpoint, data=payload)
            return response.get("deviceListItems", response.get("deviceList", []))
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
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=tz.tzutc())
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=tz.tzutc())
        except ValueError as e:
            logger.error(f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
            raise

        now = datetime.now(tz.tzutc())
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
            return self._make_request("POST", endpoint, data=payload)
        except Exception as e:
            logger.error(f"Error fetching historical data for device {device.get('deviceSn', 'unknown')}: {str(e)}")
            raise

def main():
    # Credentials
    email = "Maintenanceunit2@gspcrop.in"
    password_sha256 = "ff2612c35745d5bbdf4103f986c7279f31ff7b728da17469256ffa019f59aa9c"
    app_id = "3124071788531342"
    app_secret = "95bdc99830b61580123a96dad4bb7bc7"

    # Date range
    #start_date = "2023-05-09"
    start_date = "2024-12-20"
    end_date = "2024-12-20"

    # Time type (1 = Frame data)
    time_type = 1

    # Initialize API client
    api = SolarmanAPI(email, password_sha256, app_id, app_secret)

    try:
        # Get plants
        plants = api.get_plant_list()
        if not plants:
            logger.info("No plants found.")
            return

        for plant in plants:
            plant_id = plant.get("id", "Unknown ID")
            plant_name = plant.get("name", "Unknown Station")
            logger.info(f"Processing plant: {plant_name} (ID: {plant_id})")

            # Get devices
            devices = api.get_all_devices(plant_id)
            if not devices:
                logger.info(f"No devices found for plant: {plant_name}")
                continue

            for device in devices:
                device_sn = device.get("deviceSn", "unknown")
                if device.get("connectStatus") == 0:
                    logger.info(f"Skipping disconnected device: {device_sn}")
                    continue
                logger.info(f"Fetching historical data for device: {device_sn}")

                try:
                    # Split date range into 1-day chunks
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=tz.tzutc())
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=tz.tzutc())
                    now = datetime.now(tz.tzutc())
                    if end_dt > now:
                        end_dt = now

                    current_date = start_dt
                    csv_filename = f"historical_datax_{device_sn}_t{time_type}.csv"
                    first_write = True

                    while current_date <= end_dt:
                        chunk_date = current_date.strftime('%Y-%m-%d')
                        logger.info(f"Fetching data for {chunk_date}")
                        historical_data = api.get_historical_data(device, chunk_date, chunk_date, time_type)
                        print(f"{historical_data}");
                        if historical_data.get("paramDataList"):
                            csv_data = json_to_name_columns_csv(historical_data)
                            if csv_data:
                                mode = 'w' if first_write else 'a'
                                with open(csv_filename, mode, newline='', encoding='utf-8') as f:
                                    if first_write:
                                        f.write(csv_data)
                                    else:
                                        # Skip header for append
                                        f.write('\n'.join(csv_data.split('\n')[1:]) + '\n')
                                logger.info(f"{'Wrote' if first_write else 'Appended'} data to {csv_filename}")
                                first_write = False
                        else:
                            logger.info(f"No data for {chunk_date}")

                        current_date += timedelta(days=1)

                    if first_write:
                        logger.info(f"No data to save for device {device_sn}")
                except Exception as e:
                    logger.error(f"Failed to fetch historical data for device {device_sn}: {str(e)}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
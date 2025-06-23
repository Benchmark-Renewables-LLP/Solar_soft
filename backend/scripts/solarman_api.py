import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dateutil import tz
import requests

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

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

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
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

    def get_plant_list(self, user_id: str, username: str, password: str) -> List[Dict]:
        endpoint = "/station/v1.0/list?language=en"
        try:
            response = self._make_request("POST", endpoint, data={})
            return response.get("stationList", [])
        except Exception as e:
            logger.error(f"Error fetching plant list: {str(e)}")
            raise

    def get_all_devices(self, user_id: str, username: str, password: str, plant_id: str) -> List[Dict]:
        endpoint = "/station/v1.0/device?language=en"
        payload = {"stationId": plant_id, "deviceType": "INVERTER"}
        try:
            response = self._make_request("POST", endpoint, data=payload)
            return response.get("deviceListItems", []) or response.get("deviceList", [])
        except Exception as e:
            logger.error(f"Error fetching devices for plant {plant_id}: {str(e)}")
            raise

    def get_historical_data(self, user_id: str, username: str, password: str, device: Dict, start_date: str, end_date: str) -> List[Dict]:
        endpoint = "/device/v1.0/historical?language=en"
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=tz.tzutc())
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=tz.tzutc())
            now = datetime.now(tz.tzutc())
            if end_dt > now:
                end_dt = now
            if start_dt >= end_dt:
                raise ValueError("start_date must be before end_date")
        except ValueError as e:
            logger.error(f"Invalid date format for Solarman: {str(e)}")
            raise

        payload = {
            "deviceSn": device.get("deviceSn", ""),
            "deviceType": device.get("deviceType", "INVERTER"),
            "startTime": start_dt.strftime('%Y-%m-%d'),
            "endTime": end_dt.strftime('%Y-%m-%d'),
            "timeType": 1  # 5-minute intervals
        }
        try:
            response = self._make_request("POST", endpoint, data=payload)
            param_data_list = response.get("paramDataList", [])
            normalized_data = []
            for param_data in param_data_list:
                collect_time = param_data.get("collectTime")
                if isinstance(collect_time, (int, float)):
                    collect_time = datetime.fromtimestamp(collect_time / 1000 if len(str(int(collect_time))) > 10 else collect_time).strftime('%Y-%m-%d %H:%M:%S')
                data_list = param_data.get("dataList", [])
                entry = {"timestamp": collect_time}
                for item in data_list:
                    key = item.get("key", "").lower()
                    value = item.get("value")
                    if key in ['pv1_voltage', 'pv2_voltage', 'pv3_voltage', 'pv4_voltage', 'pv5_voltage', 'pv6_voltage', 'pv7_voltage', 'pv8_voltage', 'pv9_voltage', 'pv10_voltage', 'pv11_voltage', 'pv12_voltage']:
                        entry[key.replace('pv1_', 'pv01_').replace('pv2_', 'pv02_').replace('pv3_', 'pv03_').replace('pv4_', 'pv04_').replace('pv5_', 'pv05_').replace('pv6_', 'pv06_').replace('pv7_', 'pv07_').replace('pv8_', 'pv08_').replace('pv9_', 'pv09_')] = value
                    elif key in ['pv1_current', 'pv2_current', 'pv3_current', 'pv4_current', 'pv5_current', 'pv6_current', 'pv7_current', 'pv8_current', 'pv9_current', 'pv10_current', 'pv11_current', 'pv12_current']:
                        entry[key.replace('pv1_', 'pv01_').replace('pv2_', 'pv02_').replace('pv3_', 'pv03_').replace('pv4_', 'pv04_').replace('pv5_', 'pv05_').replace('pv6_', 'pv06_').replace('pv7_', 'pv07_').replace('pv8_', 'pv08_').replace('pv9_', 'pv09_')] = value
                    elif key in ['r_voltage', 's_voltage', 't_voltage', 'r_current', 's_current', 't_current', 'rs_voltage', 'st_voltage', 'tr_voltage']:
                        entry[key] = value
                    elif key == 'frequency':
                        entry['frequency'] = value
                    elif key in ['total_power', 'power']:
                        entry['total_power'] = value
                    elif key in ['reactive_power']:
                        entry['reactive_power'] = value
                    elif key in ['energy_today', 'e_day']:
                        entry['energy_today'] = value
                    elif key in ['pr']:
                        entry['pr'] = value
                    elif key in ['state', 'status']:
                        entry['state'] = value
                normalized_data.append(entry)
            return normalized_data
        except Exception as e:
            logger.error(f"Error fetching Solarman historical data for {device.get('deviceSn')}: {str(e)}")
            raise

    def get_current_data(self, user_id: str, username: str, password: str, device: Dict) -> List[Dict]:
        endpoint = "/device/v1.0/currentData"
        params = {"language": "en"}
        payload = {"deviceSn": device.get("deviceSn", "")}
        if "deviceId" in device:
            payload["deviceId"] = device["deviceId"]
        try:
            response = self._make_request("POST", endpoint, params=params, data=payload)
            data_list = response.get("dataList", [])
            collect_time = datetime.now(tz.tzutc()).strftime('%Y-%m-%d %H:%M:%S')
            normalized_data = []
            entry = {"timestamp": collect_time}
            for item in data_list:
                key = item.get("key", "").lower()
                value = item.get("value")
                if key in ['pv1_voltage', 'pv2_voltage', 'pv3_voltage', 'pv4_voltage', 'pv5_voltage', 'pv6_voltage', 'pv7_voltage', 'pv8_voltage', 'pv9_voltage', 'pv10_voltage', 'pv11_voltage', 'pv12_voltage']:
                    entry[key.replace('pv1_', 'pv01_').replace('pv2_', 'pv02_').replace('pv3_', 'pv03_').replace('pv4_', 'pv04_').replace('pv5_', 'pv05_').replace('pv6_', 'pv06_').replace('pv7_', 'pv07_').replace('pv8_', 'pv08_').replace('pv9_', 'pv09_')] = value
                elif key in ['pv1_current', 'pv2_current', 'pv3_current', 'pv4_current', 'pv5_current', 'pv6_current', 'pv7_current', 'pv8_current', 'pv9_current', 'pv10_current', 'pv11_current', 'pv12_current']:
                    entry[key.replace('pv1_', 'pv01_').replace('pv2_', 'pv02_').replace('pv3_', 'pv03_').replace('pv4_', 'pv04_').replace('pv5_', 'pv05_').replace('pv6_', 'pv06_').replace('pv7_', 'pv07_').replace('pv8_', 'pv08_').replace('pv9_', 'pv09_')] = value
                elif key in ['r_voltage', 's_voltage', 't_voltage', 'r_current', 's_current', 't_current', 'rs_voltage', 'st_voltage', 'tr_voltage']:
                    entry[key] = value
                elif key == 'frequency':
                    entry['frequency'] = value
                elif key in ['total_power', 'power']:
                    entry['total_power'] = value
                elif key in ['reactive_power']:
                    entry['reactive_power'] = value
                elif key in ['energy_today', 'e_day']:
                    entry['energy_today'] = value
                elif key in ['pr']:
                    entry['pr'] = value
                elif key in ['state', 'status']:
                    entry['state'] = value
            if entry.get("timestamp"):
                normalized_data.append(entry)
            return normalized_data
        except Exception as e:
            logger.error(f"Error fetching Solarman current data for {device.get('deviceSn')}: {str(e)}")
            raise
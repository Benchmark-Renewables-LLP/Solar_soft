import json
import logging
import time
import csv
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from dateutil import tz

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
    
    fieldnames = [item.get("name", "") for item in data_list]
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        lineterminator='\n',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()

    row = {item.get("name", ""): item.get("value", "") for item in data_list}
    writer.writerow(row)

    csv_content = output.getvalue()
    output.close()
    return csv_content

class SolarmanAPI:
    def __init__(self, email: str, password_sha256: str, app_id: str, app_secret: str, base_url: str = "https://globalapi.solarmanpv.com"):
        self.base_url = base_url
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
            return [
                {
                    "plant_id": p["id"],
                    "plant_name": p.get("stationName", p.get("name", "Unknown")),
                    "capacity": float(p.get("designedPower", 0)),
                    "total_energy": float(p.get("totalGeneration", 0)),
                    "install_date": p.get("createDate")
                }
                for p in response.get("stationList", [])
            ]
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
            return [
                {
                    "sn": d["deviceSn"],
                    "first_install_date": d.get("createDate"),
                    "inverter_model": d.get("deviceModel", "Unknown"),
                    "panel_model": "Unknown",
                    "pv_count": 0,
                    "string_count": 0
                }
                for d in devices
            ]
        except Exception as e:
            logger.error(f"Error fetching devices for plant {plant_id}: {str(e)}")
            raise

    def get_historical_data(
        self,
        device: Dict,
        start_date: str,
        end_date: str,
        time_type: int = 1
    ) -> List[Dict]:
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
            data_list = response.get("paramDataList", [])
            historical_data = []
            for item in data_list:
                timestamp = item.get("collectTime")
                if not timestamp:
                    continue
                try:
                    ts = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    logger.warning(f"Invalid timestamp format for device {device.get('deviceSn', 'unknown')}: {timestamp}")
                    continue
                entry = {"device_id": device["deviceSn"], "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")}
                for param in item.get("dataList", []):
                    key = param.get("key", "").lower()
                    value = param.get("value")
                    if not value or value == "":
                        continue
                    if "power" in key:
                        entry["total_power"] = float(value)
                    elif "voltage" in key and "pv1" in key:
                        entry["pv01_voltage"] = float(value)
                    elif "current" in key and "pv1" in key:
                        entry["pv01_current"] = float(value)
                    elif "state" in key or "status" in key:
                        entry["state"] = value
                    elif "energy" in key and "today" in key:
                        entry["energy_today"] = float(value)
                historical_data.append(entry)
            return historical_data
        except Exception as e:
            logger.error(f"Error fetching historical data for device {device.get('deviceSn', 'unknown')}: {str(e)}")
            raise

    def get_current_data(
        self,
        device: Dict,
        language: str = "en"
    ) -> List[Dict]:
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
            data_list = response.get("dataList", [])
            current_data = []
            timestamp = datetime.now(tz.tzutc()).strftime('%Y-%m-%d %H:%M:%S')
            for item in data_list:
                entry = {"device_id": device["deviceSn"], "timestamp": timestamp}
                key = item.get("key", "").lower()
                value = item.get("value")
                if not value or value == "":
                    continue
                if "power" in key:
                    entry["total_power"] = float(value)
                elif "voltage" in key and "pv1" in key:
                    entry["pv01_voltage"] = float(value)
                elif "current" in key and "pv1" in key:
                    entry["pv01_current"] = float(value)
                elif "state" in key or "status" in key:
                    entry["state"] = value
                elif "energy" in key and "today" in key:
                    entry["energy_today"] = float(value)
                current_data.append(entry)
            return current_data
        except Exception as e:
            logger.error(f"Error fetching current data for device {device.get('deviceSn', 'unknown')}: {str(e)}")
            raise
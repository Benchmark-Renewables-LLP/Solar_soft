import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dateutil import tz
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def get_access_token(self) -> None:
        url = f"{self.base_url}/account/v1.0/token?appId={self.app_id}"
        payload = {
            "appSecret": self.app_secret,
            "email": self.email,
            "password": self.password_sha256,
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
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
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obtaining access token: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=20),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
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
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            result = response.json()
            logger.debug(f"API response for {endpoint}: {json.dumps(result, indent=2, ensure_ascii=False)}")

            if not result.get("success"):
                logger.error(f"API request failed: {result.get('msg')}")
                raise Exception(f"API request failed: {result.get('msg')}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making API request to {endpoint}: {str(e)}")
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
            if start_dt > end_dt:
                raise ValueError("start_date must be before end_date")
        except ValueError as e:
            logger.error(f"Invalid date format for Solarman: {str(e)}")
            raise

        payload = {
            "deviceSn": device.get("deviceSn", ""),
            "deviceType": device.get("deviceType", "INVERTER"),
            "startTime": start_dt.strftime('%Y-%m-%d'),
            "endTime": end_dt.strftime('%Y-%m-%d'),
            "timeType": 1  # Assuming 1 is for daily data; adjust if needed per API docs
        }
        normalized_data = []
        try:
            response = self._make_request("POST", endpoint, data=payload)
            param_data_list = response.get("paramDataList", [])
            logger.debug(f"Raw paramDataList for {device.get('deviceSn')}: {param_data_list}")
            for param_data in param_data_list:
                collect_time = param_data.get("collectTime")
                if isinstance(collect_time, (int, float)):
                    collect_time_dt = datetime.fromtimestamp(collect_time / 1000 if len(str(int(collect_time))) > 10 else collect_time, tz=tz.tzutc())
                    if now - collect_time_dt < timedelta(minutes=5):
                        logger.debug(f"Skipping recent timestamp for device {device.get('deviceSn')}: {collect_time}")
                        continue
                    collect_time = collect_time_dt.strftime('%Y-%m-%d %H:%M:%S')
                data_list = param_data.get("dataList", [])
                if not data_list:
                    logger.warning(f"Skipping empty data entry for device {device.get('deviceSn')} at timestamp {collect_time}")
                    continue
                entry = {"timestamp": collect_time}
                for item in data_list:
                    key = item.get("key", "").lower()
                    value = item.get("value")
                    if key in ['dc1', 'dc2', 'dc3', 'dc4', 'dc5', 'dc6', 'dc7', 'dc8', 'dc9', 'dc10', 'dc11', 'dc12', 'dc13', 'dc14', 'dc15', 'dc16']:
                        pv_index = int(key.replace('dc', '')) if key.startswith('dc') else None
                        if pv_index:
                            entry[f'pv{pv_index:02d}_current'] = value
                    elif key in ['dv1', 'dv2', 'dv3', 'dv4', 'dv5', 'dv6', 'dv7', 'dv8', 'dv9', 'dv10', 'dv11', 'dv12', 'dv13', 'dv14', 'dv15', 'dv16']:
                        pv_index = int(key.replace('dv', '')) if key.startswith('dv') else None
                        if pv_index:
                            entry[f'pv{pv_index:02d}_voltage'] = value
                    elif key in ['av1', 'av2', 'av3']:
                        phase = {'av1': 'r', 'av2': 's', 'av3': 't'}.get(key)
                        if phase:
                            entry[f'{phase}_voltage'] = value
                    elif key in ['ac1', 'ac2', 'ac3']:
                        phase = {'ac1': 'r', 'ac2': 's', 'ac3': 't'}.get(key)
                        if phase:
                            entry[f'{phase}_current'] = value
                    elif key == 'tpg':
                        entry['total_power'] = value
                    elif key == 'etdy_ge1':
                        entry['energy_today'] = value
                    elif key == 'a_fo1':
                        entry['frequency'] = value
                    elif key == 'inv_st1':
                        entry['state'] = value
                    elif key == 'dpi_t1':
                        entry['total_dc_input_power'] = value
                    elif key in ['pv1_voltage', 'pv2_voltage', 'pv3_voltage', 'pv4_voltage', 'pv5_voltage', 'pv6_voltage', 'pv7_voltage', 'pv8_voltage', 'pv9_voltage', 'pv10_voltage', 'pv11_voltage', 'pv12_voltage']:
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
                    elif key in ['energy_today', 'etdy_ge1']:
                        entry['energy_today'] = value
                    elif key in ['pr']:
                        entry['pr'] = value
                    elif key in ['state', 'status', 'inv_st1']:
                        entry['state'] = value
                if len(entry) > 1:
                    normalized_data.append(entry)
                else:
                    logger.warning(f"Skipping empty data entry for device {device.get('deviceSn')} at timestamp {collect_time}")
        except Exception as e:
            logger.error(f"Error fetching Solarman historical data for {device.get('deviceSn')}: {str(e)}")
            raise
        return normalized_data

    def get_current_day_data(self, user_id: str, username: str, password: str, device: Dict) -> List[Dict]:
        endpoint = "/device/v1.0/historical?language=en"
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = datetime.now().strftime('%Y-%m-%d')
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=tz.tzutc())
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=tz.tzutc())
            now = datetime.now(tz.tzutc())
            if end_dt > now:
                end_dt = now
            if start_dt > end_dt:
                raise ValueError("start_date must be before end_date")
        except ValueError as e:
            logger.error(f"Invalid date format for Solarman: {str(e)}")
            raise

        normalized_data = []
        current_dt = start_dt
        while current_dt <= end_dt:
            payload = {
                "deviceSn": device.get("deviceSn", ""),
                "deviceType": device.get("deviceType", "INVERTER"),
                "startTime": current_dt.strftime('%Y-%m-%d'),
                "endTime": current_dt.strftime('%Y-%m-%d'),
                "timeType": 1
            }
            try:
                response = self._make_request("POST", endpoint, data=payload)
                time.sleep(1)  # Rate limit
                param_data_list = response.get("paramDataList", [])
                logger.debug(f"Raw paramDataList for {device.get('deviceSn')} on {current_dt.strftime('%Y-%m-%d')}: {json.dumps(param_data_list, indent=2, ensure_ascii=False)}")
                for param_data in param_data_list:
                    collect_time = param_data.get("collectTime")
                    if not collect_time:
                        logger.warning(f"Missing collectTime for device {device.get('deviceSn')}")
                        continue
                    if isinstance(collect_time, (int, float)):
                        try:
                            timestamp = collect_time / 1000 if len(str(int(collect_time))) > 10 else collect_time
                            collect_time_dt = datetime.fromtimestamp(timestamp, tz=tz.tzutc())
                            if now - collect_time_dt < timedelta(minutes=5):
                                logger.debug(f"Skipping recent timestamp for device {device.get('deviceSn')}: {collect_time}")
                                continue
                            collect_time = collect_time_dt.strftime('%Y-%m-%d %H:%M:%S')
                        except (ValueError, TypeError) as e:
                            logger.error(f"Invalid collectTime number format for device {device.get('deviceSn')}: {collect_time}, error: {str(e)}")
                            continue
                    elif isinstance(collect_time, str):
                        try:
                            collect_time_dt = datetime.strptime(collect_time, '%Y-%m-%d %H:%M:%S')
                            collect_time = collect_time_dt.strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                timestamp = float(collect_time)
                                timestamp = timestamp / 1000 if len(str(int(timestamp))) > 10 else timestamp
                                collect_time_dt = datetime.fromtimestamp(timestamp, tz=tz.tzutc())
                                if now - collect_time_dt < timedelta(minutes=5):
                                    logger.debug(f"Skipping recent timestamp for device {device.get('deviceSn')}: {collect_time}")
                                    continue
                                collect_time = collect_time_dt.strftime('%Y-%m-%d %H:%M:%S')
                            except (ValueError, TypeError) as e:
                                logger.error(f"Invalid string collectTime format for device {device.get('deviceSn')}: {collect_time}, error: {str(e)}")
                                continue
                    else:
                        logger.error(f"Unexpected collectTime type for device {device.get('deviceSn')}: {type(collect_time)}")
                        continue

                    data_list = param_data.get("dataList", [])
                    if not data_list:
                        logger.warning(f"Skipping empty data entry for device {device.get('deviceSn')} at timestamp {collect_time}")
                        continue
                    entry = {"timestamp": collect_time}
                    for item in data_list:
                        key = item.get("key", "").lower()
                        value = item.get("value")
                        if key in ['dc1', 'dc2', 'dc3', 'dc4', 'dc5', 'dc6', 'dc7', 'dc8', 'dc9', 'dc10', 'dc11', 'dc12', 'dc13', 'dc14', 'dc15', 'dc16']:
                            pv_index = int(key.replace('dc', '')) if key.startswith('dc') else None
                            if pv_index:
                                entry[f'pv{pv_index:02d}_current'] = value
                        elif key in ['dv1', 'dv2', 'dv3', 'dv4', 'dv5', 'dv6', 'dv7', 'dv8', 'dv9', 'dv10', 'dv11', 'dv12', 'dv13', 'dv14', 'dv15', 'dv16']:
                            pv_index = int(key.replace('dv', '')) if key.startswith('dv') else None
                            if pv_index:
                                entry[f'pv{pv_index:02d}_voltage'] = value
                        elif key in ['av1', 'av2', 'av3']:
                            phase = {'av1': 'r', 'av2': 's', 'av3': 't'}.get(key)
                            if phase:
                                entry[f'{phase}_voltage'] = value
                        elif key in ['ac1', 'ac2', 'ac3']:
                            phase = {'ac1': 'r', 'ac2': 's', 'ac3': 't'}.get(key)
                            if phase:
                                entry[f'{phase}_current'] = value
                        elif key == 'tpg':
                            entry['total_power'] = value
                        elif key == 'etdy_ge1':
                            entry['energy_today'] = value
                        elif key == 'a_fo1':
                            entry['frequency'] = value
                        elif key == 'inv_st1':
                            entry['state'] = value
                        elif key == 'dpi_t1':
                            entry['total_dc_input_power'] = value
                        elif key in ['pv1_voltage', 'pv2_voltage', 'pv3_voltage', 'pv4_voltage', 'pv5_voltage', 'pv6_voltage', 'pv7_voltage', 'pv8_voltage', 'pv9_voltage', 'pv10_voltage', 'pv11_voltage', 'pv12_voltage']:
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
                        elif key in ['energy_today', 'etdy_ge1']:
                            entry['energy_today'] = value
                        elif key in ['pr']:
                            entry['pr'] = value
                        elif key in ['state', 'status', 'inv_st1']:
                            entry['state'] = value
                    if len(entry) > 1:
                        normalized_data.append(entry)
                    else:
                        logger.warning(f"Skipping empty data entry for device {device.get('deviceSn')} at timestamp {collect_time}")
            except Exception as e:
                logger.error(f"Error fetching Solarman historical data for {device.get('deviceSn')} on {current_dt.strftime('%Y-%m-%d')}: {str(e)}")
                continue
            current_dt += timedelta(days=1)
        return normalized_data
    
    def get_realtime_data(self, user_id: str, username: str, password: str, device: Dict) -> List[Dict]:
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
                if key in ['dc1', 'dc2', 'dc3', 'dc4', 'dc5', 'dc6', 'dc7', 'dc8', 'dc9', 'dc10', 'dc11', 'dc12', 'dc13', 'dc14', 'dc15', 'dc16']:
                    pv_index = int(key.replace('dc', '')) if key.startswith('dc') else None
                    if pv_index:
                        entry[f'pv{pv_index:02d}_current'] = value
                elif key in ['dv1', 'dv2', 'dv3', 'dv4', 'dv5', 'dv6', 'dv7', 'dv8', 'dv9', 'dv10', 'dv11', 'dv12', 'dv13', 'dv14', 'dv15', 'dv16']:
                    pv_index = int(key.replace('dv', '')) if key.startswith('dv') else None
                    if pv_index:
                        entry[f'pv{pv_index:02d}_voltage'] = value
                elif key in ['av1', 'av2', 'av3']:
                    phase = {'av1': 'r', 'av2': 's', 'av3': 't'}.get(key)
                    if phase:
                        entry[f'{phase}_voltage'] = value
                elif key in ['ac1', 'ac2', 'ac3']:
                    phase = {'ac1': 'r', 'ac2': 's', 'ac3': 't'}.get(key)
                    if phase:
                        entry[f'{phase}_current'] = value
                elif key == 'tpg':
                    entry['total_power'] = value
                elif key == 'etdy_ge1':
                    entry['energy_today'] = value
                elif key == 'a_fo1':
                    entry['frequency'] = value
                elif key == 'inv_st1':
                    entry['state'] = value
                elif key == 'dpi_t1':
                    entry['total_dc_input_power'] = value
                elif key in ['pv1_voltage', 'pv2_voltage', 'pv3_voltage', 'pv4_voltage', 'pv5_voltage', 'pv6_voltage', 'pv7_voltage', 'pv8_voltage', 'pv9_voltage', 'pv10_voltage', 'pv11_voltage', 'pv12_voltage']:
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
                elif key in ['energy_today', 'etdy_ge1']:
                    entry['energy_today'] = value
                elif key in ['pr']:
                    entry['pr'] = value
                elif key in ['state', 'status', 'inv_st1']:
                    entry['state'] = value
            if len(entry) > 1:
                normalized_data.append(entry)
            else:
                logger.warning(f"Skipping empty current data entry for device {device.get('deviceSn')}")
            return normalized_data
        except Exception as e:
            logger.error(f"Error fetching Solarman current data for {device.get('deviceSn')}: {str(e)}")
            raise
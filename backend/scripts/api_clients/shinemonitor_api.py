import os
import sys
import logging
import hashlib
import time
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime, timedelta
from config.settings import COMPANY_KEY
from pytz import timezone

class ShinemonitorAPI:
    def __init__(self, company_key=None, base_url="http://api.shinemonitor.com/public/"):
        self.company_key = company_key if company_key is not None else COMPANY_KEY
        self.base_url = base_url
        self.secret = None
        self.token = None
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('shinemonitor_api.log', encoding='utf-8')
                ]
            )

    def calculate_sign(self, salt, secret_or_pwd, additional_params, is_auth=False):
        if is_auth:
            pwd_hash = hashlib.sha1(secret_or_pwd.encode('utf-8')).hexdigest()
            data = f"{salt}{pwd_hash}{additional_params}"
        else:
            data = f"{salt}{secret_or_pwd}{additional_params}"
        return hashlib.sha1(data.encode('utf-8')).hexdigest()

    def authenticate(self, username, password):
        try:
            salt = str(int(time.time() * 1000))
            action_params = f"&action=auth&usr={username}&company-key={self.company_key}"
            sign = self.calculate_sign(salt, password, action_params, is_auth=True)
            url = f"{self.base_url}?sign={sign}&salt={salt}{action_params}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("err") != 0:
                self.logger.error(f"Authentication failed: {data.get('desc')}")
                self.secret = None
                self.token = None
                return None, None

            self.secret = data["dat"]["secret"]
            self.token = data["dat"]["token"]
            self.logger.info("Authentication successful")
            return self.secret, self.token
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during authentication: {e}")
            self.secret = None
            self.token = None
            return None, None

    def fetch_plant_list(self, user_id, username, password):
        if not self.secret or not self.token:
            self.authenticate(username, password)
        if not self.secret or not self.token:
            return []

        try:
            salt = str(int(time.time() * 1000))
            action_params = "&action=queryPlants&pagesize=50"
            sign = self.calculate_sign(salt, self.secret, f"{self.token}{action_params}")
            url = f"{self.base_url}?sign={sign}&salt={salt}&token={self.token}{action_params}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("err") != 0:
                self.logger.error(f"Error fetching plant list for user {user_id}: {data.get('desc')}")
                return []

            return [
                {
                    "plant_id": p["pid"],
                    "plant_name": p.get("name"),
                    "capacity": float(p.get("nominalPower", 0)),
                    "total_energy": float(p.get("energyYearEstimate", 0)),
                    "install_date": p.get("install")
                }
                for p in data["dat"]["plant"]
            ]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching plant list for user {user_id}: {e}")
            return []

    def fetch_plant_info(self, user_id, username, password, plant_id):
        if not self.secret or not self.token:
            self.authenticate(username, password)
        if not self.secret or not self.token:
            return None

        try:
            salt = str(int(time.time() * 1000))
            action_params = f"&action=queryPlantInfo&plantid={plant_id}"
            sign = self.calculate_sign(salt, self.secret, f"{self.token}{action_params}")
            url = f"{self.base_url}?sign={sign}&salt={salt}&token={self.token}{action_params}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("err") != 0:
                self.logger.error(f"Error fetching plant info for plant {plant_id}: {data.get('desc')}")
                return None

            return {"install_date": data["dat"]["install"]}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching plant info for plant {plant_id}: {e}")
            return None

    def fetch_plant_devices(self, user_id, username, password, plant_id):
        if not self.secret or not self.token:
            self.authenticate(username, password)
        if not self.secret or not self.token:
            return []

        try:
            salt = str(int(time.time() * 1000))
            action_params = f"&action=queryDevices&plantid={plant_id}&pagesize=50"
            sign = self.calculate_sign(salt, self.secret, f"{self.token}{action_params}")
            url = f"{self.base_url}?sign={sign}&salt={salt}&token={self.token}{action_params}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("err") != 0:
                self.logger.error(f"Error fetching devices for plant {plant_id}, user {user_id}: {data.get('desc')}")
                return []

            devices = data["dat"]["device"]
            plant_info = self.fetch_plant_info(user_id, username, password, plant_id)
            install_date = plant_info.get("install_date") if plant_info else None

            return [
                {
                    "sn": d["sn"],
                    "first_install_date": install_date,
                    "inverter_model": "Unknown",
                    "panel_model": "Unknown",
                    "pn": d["pn"],
                    "devcode": d["devcode"],
                    "devaddr": d["devaddr"],
                    "pv_count": 3,
                    "string_count": 0
                }
                for d in devices
            ]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching devices for plant {plant_id}, user {user_id}: {e}")
            return []

    def fetch_historical_data(self, user_id, username, password, device, start_date, end_date):
        if not self.secret or not self.token:
            self.authenticate(username, password)
        if not self.secret or not self.token:
            return []

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            all_data = []
            current_date = start

            while current_date <= end:
                date_str = current_date.strftime('%Y-%m-%d')
                salt = str(int(time.time() * 1000))
                action_params = f"&action=queryDeviceDataOneDay&i18n=en_US&pn={device['pn']}&devcode={device['devcode']}&devaddr={device['devaddr']}&sn={device['sn']}&startDate={date_str}&endDate={date_str}"
                sign = self.calculate_sign(salt, self.secret, f"{self.token}{action_params}")
                url = f"{self.base_url}?sign={sign}&salt={salt}&token={self.token}{action_params}"

                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()

                if data.get("err") != 0:
                    self.logger.error(f"Error fetching historical data for device {device['sn']} on {date_str}: {data.get('desc')}")
                else:
                    daily_data = data["dat"]["row"]
                    self.logger.info(f"Received {len(daily_data)} data rows for device {device['sn']} on {date_str}")
                    if daily_data:
                        for row in daily_data:
                            fields = row["field"]
                            entry = {"device_id": device["sn"], "timestamp": fields[1]}
                            faults = []
                            for idx, title in enumerate(data["dat"]["title"]):
                                value = fields[idx]
                                if not value or value == "":
                                    continue
                                title_text = title["title"]

                                if any(k in title_text for k in ["PV1 input voltage", "PV1 voltage", "String 1 voltage", "DC voltage 1"]):
                                    entry["pv01_voltage"] = float(value)
                                elif any(k in title_text for k in ["PV2 input voltage", "PV2 voltage", "String 2 voltage", "DC voltage 2"]):
                                    entry["pv02_voltage"] = float(value)
                                elif any(k in title_text for k in ["PV3 input voltage", "PV3 voltage", "String 3 voltage", "DC voltage 3"]):
                                    entry["pv03_voltage"] = float(value)
                                elif any(k in title_text for k in ["PV1 Input current", "String 1 current", "DC current 1"]):
                                    entry["pv01_current"] = float(value)
                                elif any(k in title_text for k in ["PV2 Input current", "String 2 current", "DC current 2"]):
                                    entry["pv02_current"] = float(value)
                                elif any(k in title_text for k in ["PV3 Input current", "String 3 current", "DC current 3"]):
                                    entry["pv03_current"] = float(value)
                                elif "R phase grid current" in title_text or "grid current A" in title_text:
                                    entry["r_current"] = float(value)
                                elif "S phase grid current" in title_text or "grid current B" in title_text:
                                    entry["s_current"] = float(value)
                                elif "T phase grid current" in title_text or "grid current C" in title_text:
                                    entry["t_current"] = float(value)
                                elif "Grid line voltage RS" in title_text or "grid voltage AB" in title_text:
                                    entry["rs_voltage"] = float(value)
                                elif "Grid line voltage ST" in title_text or "grid voltage BC" in title_text:
                                    entry["st_voltage"] = float(value)
                                elif "Grid line voltage TR" in title_text or "grid voltage AC" in title_text:
                                    entry["tr_voltage"] = float(value)
                                elif "R phase grid voltage" in title_text or "grid voltage A" in title_text:
                                    entry["r_voltage"] = float(value)
                                elif "S phase grid voltage" in title_text or "grid voltage B" in title_text:
                                    entry["s_voltage"] = float(value)
                                elif "T phase grid voltage" in title_text or "grid voltage C" in title_text:
                                    entry["t_voltage"] = float(value)
                                elif "Grid frequency" in title_text:
                                    entry["frequency"] = float(value)
                                elif any(k in title_text for k in ["Grid connected power", "output power", "PV power generation today (kWh)"]):
                                    entry["total_power"] = float(value)
                                elif "output reactive power" in title_text or "total reactive energy" in title_text:
                                    entry["reactive_power"] = float(value)
                                elif "CUF" in title_text or "cuf" in title_text:
                                    entry["cuf"] = float(value)
                                elif "Inverter operation mode" in title_text or "running state" in title_text or "Inverter status" in title_text:
                                    entry["state"] = value
                                elif "inverter efficiency" in title_text:
                                    entry["pr"] = float(value)
                                elif "today energy" in title_text:
                                    entry["energy_today"] = float(value)
                                elif "fault information 1" in title_text and value:
                                    faults.append({"code": "FAULT_1", "description": value, "severity": "medium"})
                                elif "fault information 2" in title_text and value:
                                    faults.append({"code": "FAULT_2", "description": value, "severity": "medium"})
                                elif "fault information 3" in title_text and value:
                                    faults.append({"code": "FAULT_3", "description": value, "severity": "high"})
                                elif "fault information 4" in title_text and value:
                                    faults.append({"code": "FAULT_4", "description": value, "severity": "high"})

                            entry.update({
                                "pv01_voltage": entry.get("pv01_voltage", 0),
                                "pv01_current": entry.get("pv01_current", 0),
                                "pv02_voltage": entry.get("pv02_voltage", 0),
                                "pv02_current": entry.get("pv02_current", 0),
                                "pv03_voltage": entry.get("pv03_voltage", 0),
                                "pv03_current": entry.get("pv03_current", 0),
                                "pv04_voltage": entry.get("pv04_voltage", 0),
                                "pv04_current": entry.get("pv04_current", 0),
                                "pv05_voltage": entry.get("pv05_voltage", 0),
                                "pv05_current": entry.get("pv05_current", 0),
                                "pv06_voltage": entry.get("pv06_voltage", 0),
                                "pv06_current": entry.get("pv06_current", 0),
                                "pv07_voltage": entry.get("pv07_voltage", 0),
                                "pv07_current": entry.get("pv07_current", 0),
                                "pv08_voltage": entry.get("pv08_voltage", 0),
                                "pv08_current": entry.get("pv08_current", 0),
                                "pv09_voltage": entry.get("pv09_voltage", 0),
                                "pv09_current": entry.get("pv09_current", 0),
                                "pv10_voltage": entry.get("pv10_voltage", 0),
                                "pv10_current": entry.get("pv10_current", 0),
                                "pv11_voltage": entry.get("pv11_voltage", 0),
                                "pv11_current": entry.get("pv11_current", 0),
                                "pv12_voltage": entry.get("pv12_voltage", 0),
                                "pv12_current": entry.get("pv12_current", 0),
                                "r_current": entry.get("r_current", 0),
                                "s_current": entry.get("s_current", 0),
                                "t_current": entry.get("t_current", 0),
                                "r_voltage": entry.get("r_voltage", 0),
                                "s_voltage": entry.get("s_voltage", 0),
                                "t_voltage": entry.get("t_voltage", 0),
                                "rs_voltage": entry.get("rs_voltage", 0),
                                "st_voltage": entry.get("st_voltage", 0),
                                "tr_voltage": entry.get("tr_voltage", 0),
                                "frequency": entry.get("frequency", 0),
                                "total_power": entry.get("total_power", 0),
                                "reactive_power": entry.get("reactive_power", 0),
                                "cuf": entry.get("cuf", 0),
                                "pr": entry.get("pr", 0),
                                "state": entry.get("state", "unknown"),
                                "faults": faults
                            })
                            all_data.append(entry)
                current_date += timedelta(days=1)

            return all_data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching historical data for device {device['sn']}: {e}")
            return []

    def fetch_current_data(self, user_id, username, password, device, since=None):
        if not self.secret or not self.token:
            self.authenticate(username, password)
        if not self.secret or not self.token:
            return []

        try:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            salt = str(int(time.time() * 1000))
            action_params = f"&action=queryDeviceDataOneDay&i18n=en_US&pn={device['pn']}&devcode={device['devcode']}&devaddr={device['devaddr']}&sn={device['sn']}&date={date_str}"
            if since:
                action_params += f"&since={since}"
            sign = self.calculate_sign(salt, self.secret, f"{self.token}{action_params}")
            url = f"{self.base_url}?sign={sign}&salt={salt}&token={self.token}{action_params}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("err") != 0:
                self.logger.error(f"Error fetching current data for device {device['sn']}: {data.get('desc')}")
                return []

            rows = data["dat"]["row"]
            if not rows:
                return []

            current_data = []
            for row in rows:
                fields = row["field"]
                entry = {"device_id": device["sn"], "timestamp": fields[1]}
                faults = []
                for idx, title in enumerate(data["dat"]["title"]):
                    value = fields[idx]
                    if not value or value == "":
                        continue
                    title_text = title["title"]

                    if any(k in title_text for k in ["PV1 input voltage", "PV1 voltage", "String 1 voltage", "DC voltage 1 (V)"]):
                        entry["pv01_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV2 input voltage", "PV2 voltage", "String 2 voltage", "DC voltage 2 (V)"]):
                        entry["pv02_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV3 input voltage", "PV3 voltage", "String 3 voltage", "DC voltage 3 (V)"]):
                        entry["pv03_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV1 Input current", "String 1 current", "DC current 1 (A)"]):
                        entry["pv01_current"] = float(value)
                    elif any(k in title_text for k in ["PV2 Input current", "String 2 current", "DC current 2 (A)"]):
                        entry["pv02_current"] = float(value)
                    elif any(k in title_text for k in ["PV3 Input current", "String 3 current", "DC current 3"]):
                        entry["pv03_current"] = float(value)
                    elif "R phase grid voltage" in title_text or "grid voltage A" in title_text:
                        entry["r_voltage"] = float(value)
                    elif "S phase grid voltage" in title_text or "grid voltage B" in title_text:
                        entry["s_voltage"] = float(value)
                    elif "T phase grid voltage" in title_text or "grid voltage C" in title_text:
                        entry["t_voltage"] = float(value)
                    elif "Grid frequency" in title_text:
                        entry["frequency"] = float(value)
                    elif any(k in title_text for k in ["Grid connected power", "output power"]):
                        entry["total_power"] = float(value)
                    elif "Inverter operation mode" in title_text or "running state" in title_text:
                        entry["state"] = value
                    elif "today energy" in title_text or "energy today" in title_text:
                        entry["energy_today"] = float(value)
                    elif "output reactive power" in title_text:
                        entry["reactive_power"] = float(value)
                    elif "inverter efficiency" in title_text:
                        entry["pr"] = float(value)
                    elif "fault information 1" in title_text and value:
                        faults.append({"code": "FAULT_1", "description": value, "severity": "medium"})
                    elif "fault information 2" in title_text and value:
                        faults.append({"code": "FAULT_2", "description": value, "severity": "medium"})
                    elif "fault information 3" in title_text and value:
                        faults.append({"code": "FAULT_3", "description": value, "severity": "high"})
                    elif "fault information 4" in title_text and value:
                        faults.append({"code": "FAULT_4", "description": value, "severity": "high"})

                entry.update({
                    "pv01_voltage": entry.get("pv01_voltage", 0),
                    "pv01_current": entry.get("pv01_current", 0),
                    "pv02_voltage": entry.get("pv02_voltage", 0),
                    "pv02_current": entry.get("pv02_current", 0),
                    "pv03_voltage": entry.get("pv03_voltage", 0),
                    "pv03_current": entry.get("pv03_current", 0),
                    "pv04_voltage": entry.get("pv04_voltage", 0),
                    "pv04_current": entry.get("pv04_current", 0),
                    "pv05_voltage": entry.get("pv05_voltage", 0),
                    "pv05_current": entry.get("pv05_current", 0),
                    "pv06_voltage": entry.get("pv06_voltage", 0),
                    "pv06_current": entry.get("pv06_current", 0),
                    "pv07_voltage": entry.get("pv07_voltage", 0),
                    "pv07_current": entry.get("pv07_current", 0),
                    "pv08_voltage": entry.get("pv08_voltage", 0),
                    "pv08_current": entry.get("pv08_current", 0),
                    "pv09_voltage": entry.get("pv09_voltage", 0),
                    "pv09_current": entry.get("pv09_current", 0),
                    "pv10_voltage": entry.get("pv10_voltage", 0),
                    "pv10_current": entry.get("pv10_current", 0),
                    "pv11_voltage": entry.get("pv11_voltage", 0),
                    "pv11_current": entry.get("pv11_current", 0),
                    "pv12_voltage": entry.get("pv12_voltage", 0),
                    "pv12_current": entry.get("pv12_current", 0),
                    "r_voltage": entry.get("r_voltage", 0),
                    "s_voltage": entry.get("s_voltage", 0),
                    "t_voltage": entry.get("t_voltage", 0),
                    "r_current": entry.get("r_current", 0),
                    "s_current": entry.get("s_current", 0),
                    "t_current": entry.get("t_current", 0),
                    "rs_voltage": entry.get("rs_voltage", 0),
                    "st_voltage": entry.get("st_voltage", 0),
                    "tr_voltage": entry.get("tr_voltage", 0),
                    "frequency": entry.get("frequency", 0),
                    "total_power": entry.get("total_power", 0),
                    "reactive_power": entry.get("reactive_power", 0),
                    "energy_today": entry.get("energy_today", float(data["dat"].get("energy_today", 0))),
                    "cuf": entry.get("cuf", 0),
                    "pr": entry.get("pr", 0),
                    "state": entry.get("state", "unknown"),
                    "faults": faults
                })
                current_data.append(entry)

            return current_data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching current data for device {device['sn']}: {e}")
            return []
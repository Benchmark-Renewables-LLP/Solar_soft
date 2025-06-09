import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import requests
import logging
import hashlib
import time
from config.settings import DATABASE_URL, COMPANY_KEY

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API base URL
BASE_URL = "http://api.shinemonitor.com/public/"

def calculate_sign(salt, secret_or_pwd, additional_params, is_auth=False):
    """
    Calculate the sign parameter using SHA-1 as per Shinemonitor API.
    """
    if is_auth:
        # For authentication: sign = SHA-1(salt + SHA-1(pwd) + additional_params)
        pwd_hash = hashlib.sha1(secret_or_pwd.encode('utf-8')).hexdigest()
        data = f"{salt}{pwd_hash}{additional_params}"
    else:
        # For other requests: sign = SHA-1(salt + secret + token + additional_params)
        data = f"{salt}{secret_or_pwd}{additional_params}"
    return hashlib.sha1(data.encode('utf-8')).hexdigest()

def authenticate(username, password):
    """
    Authenticate with Shinemonitor API to obtain secret and token.
    """
    try:
        salt = str(int(time.time() * 1000))
        action_params = f"&action=auth&usr={username}&company-key={COMPANY_KEY}"
        sign = calculate_sign(salt, password, action_params, is_auth=True)
        url = f"{BASE_URL}?sign={sign}&salt={salt}{action_params}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("err") != 0:
            logging.error(f"Authentication failed: {data.get('desc')}")
            return None, None
        
        secret = data["dat"]["secret"]
        token = data["dat"]["token"]
        logging.info("Authentication successful")
        return secret, token
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during authentication: {e}")
        return None, None

def fetch_plant_list(user_id, username, password):
    """
    Fetch the list of plants for a user from Shinemonitor API.
    """
    try:
        secret, token = authenticate(username, password)
        if not secret or not token:
            return []

        salt = str(int(time.time() * 1000))
        action_params = f"&action=queryPlants&pagesize=50"
        sign = calculate_sign(salt, secret, f"{token}{action_params}")
        url = f"{BASE_URL}?sign={sign}&salt={salt}&token={token}{action_params}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("err") != 0:
            logging.error(f"Error fetching plant list for user {user_id}: {data.get('desc')}")
            return []
        
        plants = data["dat"]["plant"]
        return [
            {
                "plant_id": p["pid"],
                "customer_name": p.get("name"),  # Using plant name as customer name
                "capacity": float(p.get("nominalPower", 0)),
                "total_energy": float(p.get("energyYearEstimate", 0)),
                "install_date": p.get("install")  # To be used for devices
            }
            for p in plants
        ]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching plant list for user {user_id}: {e}")
        return []

def fetch_plant_devices(user_id, username, password, plant_id):
    """
    Fetch devices for a specific plant from Shinemonitor API.
    """
    try:
        secret, token = authenticate(username, password)
        if not secret or not token:
            return []

        salt = str(int(time.time() * 1000))
        action_params = f"&action=queryDevices&plantid={plant_id}&pagesize=50"
        sign = calculate_sign(salt, secret, f"{token}{action_params}")
        url = f"{BASE_URL}?sign={sign}&salt={salt}&token={token}{action_params}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("err") != 0:
            logging.error(f"Error fetching devices for plant {plant_id}, user {user_id}: {data.get('desc')}")
            return []
        
        devices = data["dat"]["device"]
        # Fetch plant info to get install_date
        plant_info = fetch_plant_info(user_id, username, password, plant_id)
        install_date = plant_info.get("install_date") if plant_info else None
        
        return [
            {
                "sn": d["sn"],
                "first_install_date": install_date,  # Using plant's install date
                "inverter_model": "Unknown",  # Not provided by API, placeholder
                "panel_model": "Unknown",  # Not provided by API, placeholder
                "pn": d["pn"],
                "devcode": d["devcode"],
                "devaddr": d["devaddr"],
                "pv_count": 3,  # Hardcoding as API doesn't provide; adjust based on actual data
                "string_count": 0  # Not provided, default to 0
            }
            for d in devices
        ]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching devices for plant {plant_id}, user {user_id}: {e}")
        return []

def fetch_plant_info(user_id, username, password, plant_id):
    """
    Fetch plant information to get install_date.
    """
    try:
        secret, token = authenticate(username, password)
        if not secret or not token:
            return None

        salt = str(int(time.time() * 1000))
        action_params = f"&action=queryPlantInfo&plantid={plant_id}"
        sign = calculate_sign(salt, secret, f"{token}{action_params}")
        url = f"{BASE_URL}?sign={sign}&salt={salt}&token={token}{action_params}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("err") != 0:
            logging.error(f"Error fetching plant info for plant {plant_id}: {data.get('desc')}")
            return None
        
        return {"install_date": data["dat"]["install"]}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching plant info for plant {plant_id}: {e}")
        return None

def fetch_historical_data(user_id, username, password, device, start_date, end_date):
    """
    Fetch historical 5-minute interval data for a device from Shinemonitor API.
    """
    try:
        secret, token = authenticate(username, password)
        if not secret or not token:
            return []

        from datetime import datetime, timedelta
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        current_date = start
        all_data = []
        consecutive_no_record = 0
        MAX_CONSECUTIVE_NO_RECORD = 30  # Stop after 30 days of no data

        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            salt = str(int(time.time() * 1000))
            action_params = f"&action=queryDeviceDataOneDay&i18n=en_US&pn={device['pn']}&devcode={device['devcode']}&devaddr={device['devaddr']}&sn={device['sn']}&date={date_str}"
            sign = calculate_sign(salt, secret, f"{token}{action_params}")
            url = f"{BASE_URL}?sign={sign}&salt={salt}&token={token}{action_params}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("err") != 0:
                desc = data.get("desc", "Unknown error")
                if desc == "ERR_NO_RECORD":
                    consecutive_no_record += 1
                    logging.warning(f"No historical data for device {device['sn']} on {date_str}: {desc}")
                    if consecutive_no_record >= MAX_CONSECUTIVE_NO_RECORD:
                        logging.warning(f"Stopping historical data fetch for device {device['sn']} after {MAX_CONSECUTIVE_NO_RECORD} days of no data")
                        break
                else:
                    logging.error(f"Error fetching historical data for device {device['sn']} on {date_str}: {desc}")
                current_date += timedelta(days=1)
                continue
            
            consecutive_no_record = 0  # Reset counter if we get data
            daily_data = data["dat"]["row"]
            if not daily_data:
                current_date += timedelta(days=1)
                continue

            # Process 5-minute interval data directly
            for row in daily_data:
                fields = row["field"]
                entry = {"device_id": device["sn"], "timestamp": fields[1]}  # timestamp is field[1]
                for idx, title in enumerate(data["dat"]["title"]):
                    value = fields[idx]
                    if not value or value == "":
                        continue
                    if "PV1 input voltage" in title["title"]:
                        entry["pv01_voltage"] = float(value)
                    elif "PV2 input voltage" in title["title"]:
                        entry["pv02_voltage"] = float(value)
                    elif "PV3 input voltage" in title["title"]:
                        entry["pv03_voltage"] = float(value)
                    elif "PV1 Input current" in title["title"]:
                        entry["pv01_current"] = float(value)
                    elif "PV2 Input current" in title["title"]:
                        entry["pv02_current"] = float(value)
                    elif "PV3 Input current" in title["title"]:
                        entry["pv03_current"] = float(value)
                    elif "R phase grid voltage" in title["title"]:
                        entry["r_voltage"] = float(value)
                    elif "S phase grid voltage" in title["title"]:
                        entry["s_voltage"] = float(value)
                    elif "T phase grid voltage" in title["title"]:
                        entry["t_voltage"] = float(value)
                    elif "Grid frequency" in title["title"]:
                        entry["frequency"] = float(value)
                    elif "Grid connected power" in title["title"]:
                        entry["total_power"] = float(value)
                    elif "Inverter operation mode" in title["title"]:
                        entry["state"] = value

                # Set remaining fields to None as not provided by API
                entry.update({
                    "pv03_voltage": entry.get("pv03_voltage"),
                    "pv03_current": entry.get("pv03_current"),
                    "pv04_voltage": None,
                    "pv04_current": None,
                    "pv05_voltage": None,
                    "pv05_current": None,
                    "pv06_voltage": None,
                    "pv06_current": None,
                    "pv07_voltage": None,
                    "pv07_current": None,
                    "pv08_voltage": None,
                    "pv08_current": None,
                    "pv09_voltage": None,
                    "pv09_current": None,
                    "pv10_voltage": None,
                    "pv10_current": None,
                    "pv11_voltage": None,
                    "pv11_current": None,
                    "pv12_voltage": None,
                    "pv12_current": None,
                    "r_current": None,
                    "s_current": None,
                    "t_current": None,
                    "rs_voltage": None,
                    "st_voltage": None,
                    "tr_voltage": None,
                    "reactive_power": None,
                    "energy_today": float(data["dat"].get("energy_today", 0)),
                    "cuf": None,
                    "pr": None
                })
                all_data.append(entry)
            
            current_date += timedelta(days=1)
        
        return all_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching historical data for device {device['sn']}: {e}")
        return []

def fetch_current_data(user_id, username, password, device, since=None):
    """
    Fetch current day time-series data for a device from Shinemonitor API.
    """
    try:
        secret, token = authenticate(username, password)
        if not secret or not token:
            return []

        from datetime import datetime
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        salt = str(int(time.time() * 1000))
        action_params = f"&action=queryDeviceDataOneDay&i18n=en_US&pn={device['pn']}&devcode={device['devcode']}&devaddr={device['devaddr']}&sn={device['sn']}&date={date_str}"
        sign = calculate_sign(salt, secret, f"{token}{action_params}")
        url = f"{BASE_URL}?sign={sign}&salt={salt}&token={token}{action_params}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("err") != 0:
            logging.error(f"Error fetching current data for device {device['sn']}: {data.get('desc')}")
            return []
        
        rows = data["dat"]["row"]
        if not rows:
            return []

        # Filter data since the last fetch if 'since' is provided
        if since:
            since_dt = datetime.strptime(since, "%Y-%m-%dT%H:%M:%SZ")
            rows = [row for row in rows if datetime.strptime(row["field"][1], "%Y-%m-%d %H:%M:%S") > since_dt]

        current_data = []
        for row in rows:
            fields = row["field"]
            entry = {"device_id": device["sn"], "timestamp": fields[1]}  # timestamp is field[1]
            for idx, title in enumerate(data["dat"]["title"]):
                value = fields[idx]
                if not value or value == "":
                    continue
                if "PV1 input voltage" in title["title"]:
                    entry["pv01_voltage"] = float(value)
                elif "PV2 input voltage" in title["title"]:
                    entry["pv02_voltage"] = float(value)
                elif "PV3 input voltage" in title["title"]:
                    entry["pv03_voltage"] = float(value)
                elif "PV1 Input current" in title["title"]:
                    entry["pv01_current"] = float(value)
                elif "PV2 Input current" in title["title"]:
                    entry["pv02_current"] = float(value)
                elif "PV3 Input current" in title["title"]:
                    entry["pv03_current"] = float(value)
                elif "R phase grid voltage" in title["title"]:
                    entry["r_voltage"] = float(value)
                elif "S phase grid voltage" in title["title"]:
                    entry["s_voltage"] = float(value)
                elif "T phase grid voltage" in title["title"]:
                    entry["t_voltage"] = float(value)
                elif "Grid frequency" in title["title"]:
                    entry["frequency"] = float(value)
                elif "Grid connected power" in title["title"]:
                    entry["total_power"] = float(value)
                elif "Inverter operation mode" in title["title"]:
                    entry["state"] = value

            # Set remaining fields to None as not provided by API
            entry.update({
                "pv03_voltage": entry.get("pv03_voltage"),
                "pv03_current": entry.get("pv03_current"),
                "pv04_voltage": None,
                "pv04_current": None,
                "pv05_voltage": None,
                "pv05_current": None,
                "pv06_voltage": None,
                "pv06_current": None,
                "pv07_voltage": None,
                "pv07_current": None,
                "pv08_voltage": None,
                "pv08_current": None,
                "pv09_voltage": None,
                "pv09_current": None,
                "pv10_voltage": None,
                "pv10_current": None,
                "pv11_voltage": None,
                "pv11_current": None,
                "pv12_voltage": None,
                "pv12_current": None,
                "r_current": None,
                "s_current": None,
                "t_current": None,
                "rs_voltage": None,
                "st_voltage": None,
                "tr_voltage": None,
                "reactive_power": None,
                "energy_today": float(data["dat"].get("energy_today", 0)),
                "cuf": None,
                "pr": None
            })
            current_data.append(entry)
        
        return current_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching current data for device {device['sn']}: {e}")
        return []
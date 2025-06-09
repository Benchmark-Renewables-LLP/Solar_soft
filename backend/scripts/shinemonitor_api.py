import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import requests
import logging
import hashlib
import time
import re
import difflib
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from config.settings import DATABASE_URL, COMPANY_KEY

# Set up logging with a dedicated log folder
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'shinemonitor_api.log')

# Configure logging with TimedRotatingFileHandler for daily logs
logger = logging.getLogger('ShinemonitorAPI')
logger.setLevel(logging.INFO)

# File handler (rotates daily)
file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', interval=1, backupCount=30)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# API base URL
BASE_URL = "http://api.shinemonitor.com/public/"

# Expected titles for mapping (used for difflib matching)
EXPECTED_TITLES = {
    "timestamp": "timestamp",
    "pv01_voltage": "PV 1 Voltage",
    "pv01_current": "PV 1 Current",
    "pv02_voltage": "PV 2 Voltage",
    "pv02_current": "PV 2 Current",
    "pv03_voltage": "PV 3 Voltage",
    "pv03_current": "PV 3 Current",
    "pv04_voltage": "PV 4 Voltage",
    "pv04_current": "PV 4 Current",
    "pv05_voltage": "PV 5 Voltage",
    "pv05_current": "PV 5 Current",
    "pv06_voltage": "PV 6 Voltage",
    "pv06_current": "PV 6 Current",
    "pv07_voltage": "PV 7 Voltage",
    "pv07_current": "PV 7 Current",
    "pv08_voltage": "PV 8 Voltage",
    "pv08_current": "PV 8 Current",
    "pv09_voltage": "PV 9 Voltage",
    "pv09_current": "PV 9 Current",
    "pv10_voltage": "PV 10 Voltage",
    "pv10_current": "PV 10 Current",
    "pv11_voltage": "PV 11 Voltage",
    "pv11_current": "PV 11 Current",
    "pv12_voltage": "PV 12 Voltage",
    "pv12_current": "PV 12 Current",
    "r_voltage": "R Voltage",
    "s_voltage": "S Voltage",
    "t_voltage": "T Voltage",
    "r_current": "R Current",
    "s_current": "S Current",
    "t_current": "T Current",
    "rs_voltage": "RS Voltage",
    "st_voltage": "ST Voltage",
    "tr_voltage": "TR Voltage",
    "frequency": "Frequency",
    "total_power": "Grid Power",
    "reactive_power": "Reactive Power",
    "state": "Inverter Mode"
}

# Regex patterns for mapping API titles to database fields
MAPPING_PATTERNS = [
    (re.compile(r"timestamp", re.IGNORECASE), "timestamp"),
    (re.compile(r"pv\s*(\d+)[-_]?\s*voltage", re.IGNORECASE), lambda m: f"pv{int(m.group(1)):02d}_voltage"),
    (re.compile(r"pv\s*(\d+)[-_]?\s*current", re.IGNORECASE), lambda m: f"pv{int(m.group(1)):02d}_current"),
    (re.compile(r"(r|s|t)\s*(phase)?[-_]?\s*voltage", re.IGNORECASE), lambda m: f"{m.group(1).lower()}_voltage"),
    (re.compile(r"(r|s|t)\s*(phase)?[-_]?\s*current", re.IGNORECASE), lambda m: f"{m.group(1).lower()}_current"),
    (re.compile(r"(rs|st|tr)\s*(phase)?[-_]?\s*voltage", re.IGNORECASE), lambda m: f"{m.group(1).lower()}_voltage"),
    (re.compile(r"frequency", re.IGNORECASE), "frequency"),
    (re.compile(r"grid\s*(connected)?[-_]?\s*power", re.IGNORECASE), "total_power"),
    (re.compile(r"reactive\s*power", re.IGNORECASE), "reactive_power"),
    (re.compile(r"inverter\s*(operation)?[-_]?\s*mode", re.IGNORECASE), "state"),
]

# Store unmapped titles for manual review
UNMAPPED_TITLES = {}

def map_api_title_to_db_field(api_title):
    """
    Map API title to database field using regex patterns and difflib for fallback.
    Returns the corresponding database field name or None if no match.
    """
    # Try regex mapping first
    for pattern, db_field_template in MAPPING_PATTERNS:
        match = pattern.match(api_title)
        if match:
            if isinstance(db_field_template, str):
                return db_field_template
            return db_field_template(match)
    
    # Fallback: Use difflib to find the closest match
    api_title_lower = api_title.lower()
    expected_titles = {k: v.lower() for k, v in EXPECTED_TITLES.items() if k != "timestamp"}
    matches = difflib.get_close_matches(api_title_lower, expected_titles.values(), n=1, cutoff=0.8)
    
    if matches:
        matched_title = matches[0]
        for db_field, expected_title in expected_titles.items():
            if expected_title == matched_title:
                logger.info(f"Dynamically mapped API title '{api_title}' to field '{db_field}' using difflib")
                return db_field
    
    # Log unmapped titles
    logger.warning(f"Unmapped API title: {api_title}")
    UNMAPPED_TITLES[api_title] = UNMAPPED_TITLES.get(api_title, 0) + 1
    return None

def calculate_sign(salt, secret_or_pwd, additional_params, is_auth=False):
    """
    Calculate the sign parameter using SHA-1 as per Shinemonitor API.
    """
    if is_auth:
        pwd_hash = hashlib.sha1(secret_or_pwd.encode('utf-8')).hexdigest()
        data = f"{salt}{pwd_hash}{additional_params}"
    else:
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
            logger.error(f"Authentication failed: {data.get('desc')}")
            return None, None
        
        secret = data["dat"]["secret"]
        token = data["dat"]["token"]
        logger.info("Authentication successful")
        return secret, token
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during authentication: {e}")
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
            logger.error(f"Error fetching plant list for user {user_id}: {data.get('desc')}")
            return []
        
        plants = data["dat"]["plant"]
        return [
            {
                "plant_id": p["pid"],
                "customer_name": p.get("name"),
                "capacity": float(p.get("nominalPower", 0)),
                "total_energy": float(p.get("energyYearEstimate", 0)),
                "install_date": p.get("install")
            }
            for p in plants
        ]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching plant list for user {user_id}: {e}")
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
            logger.error(f"Error fetching devices for plant {plant_id}, user {user_id}: {data.get('desc')}")
            return []
        
        devices = data["dat"]["device"]
        plant_info = fetch_plant_info(user_id, username, password, plant_id)
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
        logger.error(f"Error fetching devices for plant {plant_id}, user {user_id}: {e}")
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
            logger.error(f"Error fetching plant info for plant {plant_id}: {data.get('desc')}")
            return None
        
        return {"install_date": data["dat"]["install"]}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching plant info for plant {plant_id}: {e}")
        return None

def fetch_historical_data(user_id, username, password, device, start_date, end_date):
    """
    Fetch historical 5-minute interval data for a device from Shinemonitor API.
    start_date and end_date can now include time (e.g., "2025-06-09 12:00:00").
    """
    try:
        secret, token = authenticate(username, password)
        if not secret or not token:
            return []

        # Parse start_date and end_date with or without time
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            start_dt = start_dt.replace(hour=0, minute=0, second=0)
            end_dt = end_dt.replace(hour=23, minute=59, second=59)

        # Determine the date range for API calls (we need full days)
        start = start_dt.date()
        end = end_dt.date()
        current_date = start
        all_data = []
        consecutive_no_record = 0
        MAX_CONSECUTIVE_NO_RECORD = 30

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
                    logger.warning(f"No historical data for device {device['sn']} on {date_str}: {desc}")
                    if consecutive_no_record >= MAX_CONSECUTIVE_NO_RECORD:
                        logger.warning(f"Stopping historical data fetch for device {device['sn']} after {MAX_CONSECUTIVE_NO_RECORD} days of no data")
                        break
                else:
                    logger.error(f"Error fetching historical data for device {device['sn']} on {date_str}: {desc}")
                current_date += timedelta(days=1)
                continue
            
            consecutive_no_record = 0
            daily_data = data["dat"]["row"]
            logger.info(f"Received {len(daily_data)} data rows for device {device['sn']} on {date_str}")
            print(f"Received {len(daily_data)} data rows for device {device['sn']} on {date_str}")

            # Filter data within the specified time range
            daily_data = [
                row for row in daily_data
                if start_dt <= datetime.strptime(row["field"][1], "%Y-%m-%d %H:%M:%S") <= end_dt
            ]
            logger.info(f"Filtered to {len(daily_data)} rows within time range {start_dt} to {end_dt}")
            print(f"Filtered to {len(daily_data)} rows within time range {start_dt} to {end_dt}")

            if not daily_data:
                current_date += timedelta(days=1)
                continue

            # Log the titles returned by the API
            titles = [title["title"] for title in data["dat"]["title"]]
            logger.info(f"API titles for device {device['sn']} on {date_str}: {titles}")
            print(f"API titles for device {device['sn']} on {date_str}: {titles}")

            # Process 5-minute interval data
            for row in daily_data:
                fields = row["field"]
                entry = {"device_id": device["sn"], "timestamp": fields[1]}
                for idx, title in enumerate(data["dat"]["title"]):
                    api_title = title["title"]
                    value = fields[idx]
                    if not value or value == "":
                        continue
                    db_field = map_api_title_to_db_field(api_title)
                    if db_field and db_field != "timestamp":
                        try:
                            entry[db_field] = float(value) if db_field not in ["state"] else value
                        except ValueError:
                            logger.warning(f"Could not convert value '{value}' to float for field {db_field}")
                            continue

                # Set remaining fields to None as not provided by API
                entry.update({
                    "pv01_voltage": entry.get("pv01_voltage"),
                    "pv01_current": entry.get("pv01_current"),
                    "pv02_voltage": entry.get("pv02_voltage"),
                    "pv02_current": entry.get("pv02_current"),
                    "pv03_voltage": entry.get("pv03_voltage"),
                    "pv03_current": entry.get("pv03_current"),
                    "pv04_voltage": entry.get("pv04_voltage"),
                    "pv04_current": entry.get("pv04_current"),
                    "pv05_voltage": entry.get("pv05_voltage"),
                    "pv05_current": entry.get("pv05_current"),
                    "pv06_voltage": entry.get("pv06_voltage"),
                    "pv06_current": entry.get("pv06_current"),
                    "pv07_voltage": entry.get("pv07_voltage"),
                    "pv07_current": entry.get("pv07_current"),
                    "pv08_voltage": entry.get("pv08_voltage"),
                    "pv08_current": entry.get("pv08_current"),
                    "pv09_voltage": entry.get("pv09_voltage"),
                    "pv09_current": entry.get("pv09_current"),
                    "pv10_voltage": entry.get("pv10_voltage"),
                    "pv10_current": entry.get("pv10_current"),
                    "pv11_voltage": entry.get("pv11_voltage"),
                    "pv11_current": entry.get("pv11_current"),
                    "pv12_voltage": entry.get("pv12_voltage"),
                    "pv12_current": entry.get("pv12_current"),
                    "r_voltage": entry.get("r_voltage"),
                    "s_voltage": entry.get("s_voltage"),
                    "t_voltage": entry.get("t_voltage"),
                    "r_current": entry.get("r_current"),
                    "s_current": entry.get("s_current"),
                    "t_current": entry.get("t_current"),
                    "rs_voltage": entry.get("rs_voltage"),
                    "st_voltage": entry.get("st_voltage"),
                    "tr_voltage": entry.get("tr_voltage"),
                    "frequency": entry.get("frequency"),
                    "total_power": entry.get("total_power"),
                    "reactive_power": entry.get("reactive_power"),
                    "energy_today": float(data["dat"].get("energy_today", 0)),
                    "cuf": None,
                    "pr": None,
                    "state": entry.get("state")
                })
                all_data.append(entry)
            
            current_date += timedelta(days=1)
        
        return all_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching historical data for device {device['sn']}: {e}")
        return []

def fetch_current_data(user_id, username, password, device, since=None):
    """
    Fetch current day time-series data for a device from Shinemonitor API.
    """
    try:
        secret, token = authenticate(username, password)
        if not secret or not token:
            return []

        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        salt = str(int(time.time() * 1000))
        action_params = f"&action=queryDeviceDataOneDay&i18n=en_US&pn={device['pn']}&devcode={device['devcode']}&devaddr={device['devaddr']}&sn={device['sn']}&date={date_str}"
        sign = calculate_sign(salt, secret, f"{token}{action_params}")
        url = f"{BASE_URL}?sign={sign}&salt={salt}&token={token}{action_params}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("err") != 0:
            logger.error(f"Error fetching current data for device {device['sn']}: {data.get('desc')}")
            return []
        
        rows = data["dat"]["row"]
        if not rows:
            return []

        # Filter data since the last fetch if 'since' is provided
        if since:
            since_dt = datetime.strptime(since, "%Y-%m-%dT%H:%M:%SZ")
            rows = [row for row in rows if datetime.strptime(row["field"][1], "%Y-%m-%d %H:%M:%S") > since_dt]

        # Log the titles returned by the API
        titles = [title["title"] for title in data["dat"]["title"]]
        logger.info(f"API titles for device {device['sn']} (current data): {titles}")
        print(f"API titles for device {device['sn']} (current data): {titles}")

        current_data = []
        for row in rows:
            fields = row["field"]
            entry = {"device_id": device["sn"], "timestamp": fields[1]}
            for idx, title in enumerate(data["dat"]["title"]):
                api_title = title["title"]
                value = fields[idx]
                if not value or value == "":
                    continue
                db_field = map_api_title_to_db_field(api_title)
                if db_field and db_field != "timestamp":
                    try:
                        entry[db_field] = float(value) if db_field not in ["state"] else value
                    except ValueError:
                        logger.warning(f"Could not convert value '{value}' to float for field {db_field}")
                        continue

            # Set remaining fields to None as not provided by API
            entry.update({
                "pv01_voltage": entry.get("pv01_voltage"),
                "pv01_current": entry.get("pv01_current"),
                "pv02_voltage": entry.get("pv02_voltage"),
                "pv02_current": entry.get("pv02_current"),
                "pv03_voltage": entry.get("pv03_voltage"),
                "pv03_current": entry.get("pv03_current"),
                "pv04_voltage": entry.get("pv04_voltage"),
                "pv04_current": entry.get("pv04_current"),
                "pv05_voltage": entry.get("pv05_voltage"),
                "pv05_current": entry.get("pv05_current"),
                "pv06_voltage": entry.get("pv06_voltage"),
                "pv06_current": entry.get("pv06_current"),
                "pv07_voltage": entry.get("pv07_voltage"),
                "pv07_current": entry.get("pv07_current"),
                "pv08_voltage": entry.get("pv08_voltage"),
                "pv08_current": entry.get("pv08_current"),
                "pv09_voltage": entry.get("pv09_voltage"),
                "pv09_current": entry.get("pv09_current"),
                "pv10_voltage": entry.get("pv10_voltage"),
                "pv10_current": entry.get("pv10_current"),
                "pv11_voltage": entry.get("pv11_voltage"),
                "pv11_current": entry.get("pv11_current"),
                "pv12_voltage": entry.get("pv12_voltage"),
                "pv12_current": entry.get("pv12_current"),
                "r_voltage": entry.get("r_voltage"),
                "s_voltage": entry.get("s_voltage"),
                "t_voltage": entry.get("t_voltage"),
                "r_current": entry.get("r_current"),
                "s_current": entry.get("s_current"),
                "t_current": entry.get("t_current"),
                "rs_voltage": entry.get("rs_voltage"),
                "st_voltage": entry.get("st_voltage"),
                "tr_voltage": entry.get("tr_voltage"),
                "frequency": entry.get("frequency"),
                "total_power": entry.get("total_power"),
                "reactive_power": entry.get("reactive_power"),
                "energy_today": float(data["dat"].get("energy_today", 0)),
                "cuf": None,
                "pr": None,
                "state": entry.get("state")
            })
            current_data.append(entry)
        
        return current_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching current data for device {device['sn']}: {e}")
        return []
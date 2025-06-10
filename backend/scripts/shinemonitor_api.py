import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import requests
import logging
import hashlib
import time
from config.settings import DATABASE_URL,COMPANY_KEY

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
            logging.info(f"Received {len(daily_data)} data rows for device {device['sn']} on {date_str}")
            print(f"Received {len(daily_data)} data rows for device {device['sn']} on {date_str}")
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
                        continue #device_sn,install_date,id,Timestamp,serial number,control firmware version,communication firmware version,safety regulation,rated power (W),number of MPPT channel and phase,initial power (W),self-checking time (S),min threshold insulation resistance (KΩ),max threshold DC voltage (V),max threshold grid voltage (V),min threshold grid voltage (V),max threshold grid freqecncy (Hz),min threshold grid freqecncy (Hz),max threshold grid current (A),max threshold inital voltage (V),min threshold inital voltage (V),max threshold MPPT voltage (V),min threshold MPPT voltage (V),max threshold inverter temperature (°C),power factor tune,active power factor tune (%),reactive power tune (%),apparent power tune (%),on/off flag,factory reset flag,self-checking flag,anti-islanding protection flag,grid management flag,GFDI flag,RCD flag,RISO flag,GFDI earthing flag,PV curve flag,LVRT flag,EEPROM inital flag,firmware upgrade flag,running state,today energy (kWh),total reactive energy (kVarh),total reactive energy (kVarh),today grid-connected time (S),total energy (kWh),total operating time (Hour),inverter efficiency (%),grid voltage AB (V),grid voltage BC (V),grid voltage AC (V),grid voltage A (V),grid voltage B (V),grid voltage C (V),grid current A (A),grid current B (A),grid current C (A),grid frequency (Hz),input power (W),output apparent power (VA),output power (W),output reactive power (Var),radiator mode 1 temperature (°C),IGBT  mode temperature (°C),inductor temperature 1 (°C),inductor temperature 2 (°C),transformer temperature (°C),ambient temperature (°C),GFDI1 ground current (A),GFDI2 ground current (A),RCD drain current (A),DC voltage 1 (V),DC current 1 (A),DC voltage 2 (V),DC current 2 (A),DC voltage 3 (V),DC current 3 (A),DC voltage 4 (V),DC current 4 (A),fault information 1,fault information 2,fault information 3,fault information 4

                    # Define aliases for field matching
                    title_text = title["title"]

                    if any(k in title_text for k in ["PV1 input voltage", "PV1 voltage","String 1 voltage", "DC voltage 1"]):
                        entry["pv01_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV2 input voltage", "PV2 voltage", "String 2 voltage","DC voltage 2"]):
                        entry["pv02_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV3 input voltage", "PV3 voltage", "String 3 voltage","DC voltage 3"]):
                        entry["pv03_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV1 Input current", "String 1 current", "DC current 1"]):
                        entry["pv01_current"] = float(value)
                    elif any(k in title_text for k in ["PV2 Input current", "String 2 current", "DC current 2"]):
                        entry["pv02_current"] = float(value)
                    elif any(k in title_text for k in ["PV3 Input current", "String 3 current", "DC current 3"]):
                        entry["pv03_current"] = float(value)
                    elif any(k in title_text for k in ["PV4 input voltage", "PV4 voltage", "String 4 voltage", "DC voltage 4"]):
                        entry["pv04_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV5 input voltage", "PV5 voltage", "String 5 voltage", "DC voltage 5"]):
                        entry["pv05_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV6 input voltage", "PV6 voltage", "String 6 voltage", "DC voltage 6"]):
                        entry["pv06_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV7 input voltage", "PV7 voltage", "String 7 voltage", "DC voltage 7"]):
                        entry["pv07_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV8 input voltage", "PV8 voltage", "String 8 voltage", "DC voltage 8"]):
                        entry["pv08_voltage"] = float(value)  
                    elif any(k in title_text for k in ["PV9 input voltage", "PV9 voltage", "String 9 voltage", "DC voltage 9"]):
                        entry["pv09_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV10 input voltage", "PV10 voltage", "String 10 voltage", "DC voltage 10"]):
                        entry["pv10_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV11 input voltage", "PV11 voltage", "String 11 voltage", "DC voltage 11"]):
                        entry["pv11_voltage"] = float(value)
                    elif any(k in title_text for k in ["PV12 input voltage", "PV12 voltage", "String 12 voltage", "DC voltage 12"]):
                        entry["pv12_voltage"] = float(value)
                    elif "R phase grid current" in title_text or "grid current A" in title_text :
                        entry["r_current"] = float(value)
                    elif "S phase grid current" in title_text or "grid current B" in title_text :
                        entry["s_current"] = float(value)
                    elif "T phase grid current" in title_text or "grid current C" in title_text :
                        entry["t_current"] = float(value)
                    elif "Grid line voltage RS" in title_text or "grid voltage AB" in title_text:
                        entry["rs_voltage"] = float(value)
                    elif "Grid line voltage ST" in title_text or "grid voltage BC" in title_text:
                        entry["st_voltage"] = float(value)
                    elif "Grid line voltage TR" in title_text or "grid voltage AC" in title_text:
                        entry["tr_voltage"] = float(value)
                    elif "R phase grid voltage" in title_text or "grid voltage A" in title_text  or "R phase grid voltage" in title_text:
                        entry["r_voltage"] = float(value)
                    elif "S phase grid voltage" in title_text or "grid voltage B" in title_text or "S phase grid voltage" in title_text:
                        entry["s_voltage"] = float(value)
                    elif "T phase grid voltage" in title_text or "grid voltage C" in title_text or "T phase grid voltage" in title_text:
                        entry["t_voltage"] = float(value)
                    elif "Grid frequency" in title_text or "grid frequency" in title_text:
                        entry["frequency"] = float(value)
                    elif any(k in title_text for k in ["Grid connected power", "output power","PV power generation today (kWh)"]):
                        entry["total_power"] = float(value)
                    elif "PV power generation today (kWh)" in title_text or "today energy" in title_text:
                        entry["energy_today"] = float(value)
                    elif "output reactive power" in title_text or "total reactive energy" in title_text:
                        entry["reactive_power"] = float(value)
                    elif "CUF" in title_text or "cuf" in title_text:
                        entry["cuf"] = value
                  
                    elif "Inverter operation mode" in title_text or "running state" in title_text or "Inverter status" in title_text:
                        entry["state"] = value


                # Set remaining fields to None as not provided by API
                entry.update({
                    "pv03_voltage": entry.get("pv03_voltage",0),
                    "pv03_current": entry.get("pv03_current",0),
                    "pv04_voltage": entry.get("pv04_voltage",0),
                    "pv04_current": entry.get("pv04_current",0),
                    "pv05_voltage": entry.get("pv05_voltage",0),
                    "pv05_current": entry.get("pv05_current",0),
                    "pv06_voltage": entry.get("pv06_voltage",0),
                    "pv06_current": entry.get("pv06_current",0),
                    "pv07_voltage": entry.get("pv07_voltage",0),
                    "pv07_current": entry.get("pv07_current",0),
                    "pv08_voltage": entry.get("pv08_voltage",0),
                    "pv08_current": entry.get("pv08_current",0),
                    "pv09_voltage": entry.get("pv09_voltage",0),
                    "pv09_current": entry.get("pv09_current",0),
                    "pv10_voltage": entry.get("pv10_voltage",0),
                    "pv10_current": entry.get("pv10_current",0),
                    "pv11_voltage": entry.get("pv11_voltage",0),
                    "pv11_current": entry.get("pv11_current",0),
                    "pv12_voltage": entry.get("pv12_voltage",0),
                    "pv12_current": entry.get("pv12_current",0),
                    "r_current": entry.get("r_current",0),
                    "s_current": entry.get("s_current",0),
                    "t_current": entry.get("t_current",0),
                    "r_voltage": entry.get("r_voltage",0),
                    "s_voltage": entry.get("s_voltage",0),
                    "t_voltage": entry.get("t_voltage",0),
                    "rs_voltage": entry.get("rs_voltage",0),
                    "st_voltage": entry.get("st_voltage",0),
                    "tr_voltage": entry.get("tr_voltage",0),
                    "reactive_power": entry.get("reactive_power",0),
                    "energy_today": float(data["dat"].get("energy_today", 0)),
                    "cuf": entry.get("cuf",0),
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
                    # Define aliases for field matching
                title_text = title["title"]#device_sn,install_date,id,Timestamp,serial number,control firmware version,communication firmware version,safety regulation,rated power (W),number of MPPT channel and phase,initial power (W),self-checking time (S),min threshold insulation resistance (KΩ),max threshold DC voltage (V),max threshold grid voltage (V),min threshold grid voltage (V),max threshold grid freqecncy (Hz),min threshold grid freqecncy (Hz),max threshold grid current (A),max threshold inital voltage (V),min threshold inital voltage (V),max threshold MPPT voltage (V),min threshold MPPT voltage (V),max threshold inverter temperature (°C),power factor tune,active power factor tune (%),reactive power tune (%),apparent power tune (%),on/off flag,factory reset flag,self-checking flag,anti-islanding protection flag,grid management flag,GFDI flag,RCD flag,RISO flag,GFDI earthing flag,PV curve flag,LVRT flag,EEPROM inital flag,firmware upgrade flag,running state,today energy (kWh),total reactive energy (kVarh),total reactive energy (kVarh),today grid-connected time (S),total energy (kWh),total operating time (Hour),inverter efficiency (%),grid voltage AB (V),grid voltage BC (V),grid voltage AC (V),grid voltage A (V),grid voltage B (V),grid voltage C (V),grid current A (A),grid current B (A),grid current C (A),grid frequency (Hz),input power (W),output apparent power (VA),output power (W),output reactive power (Var),radiator mode 1 temperature (°C),IGBT  mode temperature (°C),inductor temperature 1 (°C),inductor temperature 2 (°C),transformer temperature (°C),ambient temperature (°C),GFDI1 ground current (A),GFDI2 ground current (A),RCD drain current (A),DC voltage 1 (V),DC current 1 (A),DC voltage 2 (V),DC current 2 (A),DC voltage 3 (V),DC current 3 (A),DC voltage 4 (V),DC current 4 (A),fault information 1,fault information 2,fault information 3,fault information 4

                if any(k in title_text for k in ["PV1 input voltage", "PV1 voltage", "String 1 voltage", "DC voltage 1 (V)"]):
                    entry["pv01_voltage"] = float(value)
                elif any(k in title_text for k in ["PV2 input voltage", "PV2 voltage", "Strin   2 voltage","DC voltage 2 (V)"]):
                    entry["pv02_voltage"] = float(value)
                elif any(k in title_text for k in ["PV3 input voltage", "PV3 voltage", "Strin   3 voltage","DC voltage 3 (V)"]):
                    entry["pv03_voltage"] = float(value)
                elif any(k in title_text for k in ["PV1 Input current", "String 1 current", "D  current 1 (A)"]):
                    entry["pv01_current"] = float(value)
                elif any(k in title_text for k in ["PV2 Input current", "String 2 current", "D  current 2 (A)"]):
                    entry["pv02_current"] = float(value)
                elif any(k in title_text for k in ["PV3 Input current", "String 3 current", "D  current 3"]):
                    entry["pv03_current"] = float(value)
                elif "R phase grid voltage" in title_text or "grid voltage A" in title_text:
                    entry["r_voltage"] = float(value)
                elif "S phase grid voltage" in title_text or "grid voltage B" in title_text:
                    entry["s_voltage"] = float(value)
                elif "T phase grid voltage" in title_text or "grid voltage C" in title_text:
                    entry["t_voltage"] = float(value)
                elif "Grid frequency" in title_text or "grid frequency" in title_text:
                    entry["frequency"] = float(value)
                elif any(k in title_text for k in ["Grid connected power", "output power"]):
                    entry["total_power"] = float(value)
                elif "Inverter operation mode" in title_text or "running state" in title_text:
                    entry["state"] = value
                elif "today energy (kwh)" in title_text:
                    entry["energy_today"] = float(value)
                elif "output reactive power" in title_text:
                    entry["reactive_power"] = float(value)

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
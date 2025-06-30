import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import logging
import json
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_KEY = "Q3M7I3K7LFWUQ9VUE5KQWLN961V92WUE"  # Your SolarEdge API key
SITE_ID = "3744591"  # Your SolarEdge site ID
API_BASE_URL = "https://monitoringapi.solaredge.com"

# Calculate date range for the past 6 months
end_date = datetime.now().date()
start_date = end_date - timedelta(days=15)  # 1 day ago

def check_site_validity():
    """Check if the site ID is valid and accessible with the API key."""
    url = f"{API_BASE_URL}/sites/list"
    params = {"api_key": API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        sites = response.json().get("sites", {}).get("site", [])
        site_ids = [str(site["id"]) for site in sites]
        if SITE_ID in site_ids:
            logger.info(f"Site ID {SITE_ID} is valid and accessible.")
            return True
        else:
            logger.error(f"Site ID {SITE_ID} not found in accessible sites: {site_ids}")
            return False
    except requests.RequestException as e:
        logger.error(f"Error validating site ID: {e}")
        return False

def fetch_data_period(site_id):
    """Fetch the data period for the site to check if it has transmitted data."""
    url = f"{API_BASE_URL}/site/{site_id}/dataPeriod"
    params = {"api_key": API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json().get("dataPeriod", {})
        logger.info(f"Data period for site {site_id}: {data}")
        return data
    except requests.RequestException as e:
        logger.error(f"Error fetching data period: {e}")
        return {}

def fetch_inventory(site_id):
    """Fetch the inventory of a site to get the list of inverters."""
    url = f"{API_BASE_URL}/site/{site_id}/inventory"
    params = {"api_key": API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json().get("Inventory", {}).get("inverters", [])
        logger.info(f"Fetched {len(data)} inverters for site {site_id}: {[inv['SN'] for inv in data]}")
        return data
    except requests.RequestException as e:
        logger.error(f"Error fetching inventory: {e}")
        if response.status_code == 403:
            logger.error("403 Forbidden: Check API key permissions or site ID.")
        elif response.status_code == 429:
            logger.error("429 Too Many Requests: API rate limit exceeded.")
        return []

def fetch_inverter_data(site_id, serial_number, start_time, end_time):
    """Fetch technical data for a specific inverter."""
    # Ensure correct date-time format (YYYY-MM-DD hh:mm:ss with space)
    start_time = start_time.replace("+", " ") if "+" in start_time else start_time
    end_time = end_time.replace("+", " ") if "+" in end_time else end_time
    url = f"{API_BASE_URL}/equipment/{site_id}/{serial_number}/data"
    params = {
        "startTime": start_time,
        "endTime": end_time,
        "api_key": API_KEY
    }
    # Explicitly encode parameters to ensure spaces are %20
    encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    full_url = f"{url}?{encoded_params}"
    try:
        logger.debug(f"Sending request to: {full_url}")
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json().get("data", {}).get("telemetries", [])
        logger.info(f"Fetched {len(data)} telemetry data points for inverter {serial_number}")
        return data
    except requests.RequestException as e:
        logger.error(f"Error fetching inverter data for {serial_number}: {e}")
        if response.status_code == 400:
            try:
                error_details = response.json()
                logger.error(f"400 Bad Request details: {error_details}")
            except ValueError:
                logger.error(f"400 Bad Request: No JSON response. URL: {full_url}")
        elif response.status_code == 403:
            logger.error("403 Forbidden: Check API key permissions or serial number.")
        elif response.status_code == 429:
            logger.error("429 Too Many Requests: API rate limit exceeded.")
        return []

def save_to_csv(data, filename, columns):
    """Save data to a CSV file using pandas."""
    if data:
        df = pd.DataFrame(data)
        if not df.empty:
            df.to_csv(filename, index=False, columns=columns)
            logger.info(f"Data saved to {filename}")
        else:
            logger.warning(f"No data to save for {filename}")
    else:
        logger.warning(f"No data to save for {filename}")

def main():
    # Create output directory
    output_dir = "solaredge_inverter_data"
    os.makedirs(output_dir, exist_ok=True)

    # Validate site ID
    if not check_site_validity():
        logger.error("Exiting due to invalid site ID or API key.")
        return

    # Check data period
    data_period = fetch_data_period(SITE_ID)
    if data_period.get("startDate") is None:
        logger.error(f"Site {SITE_ID} has no data transmission (startDate is None). Cannot fetch inverter data. Check site status in SolarEdge monitoring platform.")
        return

    # Fetch inventory to get inverters
    inverters = fetch_inventory(SITE_ID)
    if not inverters:
        logger.error("No inverters found or error fetching inventory. Exiting.")
        return

    # Validate inverter serial number
    inverter_serials = [inverter.get("SN", "") for inverter in inverters]
    target_serial = "7E1ED231-9F"
    if target_serial not in inverter_serials:
        logger.error(f"Inverter serial number {target_serial} not found in site {SITE_ID}. Available inverters: {inverter_serials}")
        return

    # Inverter Technical Data API is limited to 7 days per call
    date_ranges = []
    current_date = start_date
    while current_date < end_date:
        chunk_end = min(current_date + timedelta(days=7), end_date)
        date_ranges.append((current_date.strftime("%Y-%m-%d 00:00:00"), chunk_end.strftime("%Y-%m-%d 23:59:59")))
        current_date = chunk_end + timedelta(days=1)

    # Process each inverter
    for inverter in inverters:
        serial_number = inverter.get("SN", "")
        inverter_name = inverter.get("name", serial_number)
        logger.info(f"Processing inverter: {inverter_name} (Serial: {serial_number})")
        
        # Collect all data for this inverter
        all_data = []
        for start_time, end_time in date_ranges:
            data = fetch_inverter_data(SITE_ID, serial_number, start_time, end_time)
            if data:
                for entry in data:
                    # Flatten the telemetry data
                    flattened = {
                        "date": entry.get("date"),
                        "totalActivePower": entry.get("totalActivePower"),
                        "dcVoltage": entry.get("dcVoltage"),
                        "groundFaultResistance": entry.get("groundFaultResistance"),
                        "powerLimit": entry.get("powerLimit"),
                        "totalEnergy": entry.get("totalEnergy"),
                        "temperature": entry.get("temperature"),
                        "inverterMode": entry.get("inverterMode"),
                        "operationMode": entry.get("operationMode"),
                        "L1_acCurrent": entry.get("L1Data", {}).get("acCurrent"),
                        "L1_acVoltage": entry.get("L1Data", {}).get("acVoltage"),
                        "L1_acFrequency": entry.get("L1Data", {}).get("acFrequency"),
                        "L1_apparentPower": entry.get("L1Data", {}).get("apparentPower"),
                        "L1_activePower": entry.get("L1Data", {}).get("activePower"),
                        "L1_reactivePower": entry.get("L1Data", {}).get("reactivePower"),
                        "L1_cosPhi": entry.get("L1Data", {}).get("cosPhi"),
                        "L2_acCurrent": entry.get("L2Data", {}).get("acCurrent"),
                        "L2_acVoltage": entry.get("L2Data", {}).get("acVoltage"),
                        "L2_acFrequency": entry.get("L2Data", {}).get("acFrequency"),
                        "L2_apparentPower": entry.get("L2Data", {}).get("apparentPower"),
                        "L2_activePower": entry.get("L2Data", {}).get("activePower"),
                        "L2_reactivePower": entry.get("L2Data", {}).get("reactivePower"),
                        "L2_cosPhi": entry.get("L2Data", {}).get("cosPhi"),
                        "L3_acCurrent": entry.get("L3Data", {}).get("acCurrent"),
                        "L3_acVoltage": entry.get("L3Data", {}).get("acVoltage"),
                        "L3_acFrequency": entry.get("L3Data", {}).get("acFrequency"),
                        "L3_apparentPower": entry.get("L3Data", {}).get("apparentPower"),
                        "L3_activePower": entry.get("L3Data", {}).get("activePower"),
                        "L3_reactivePower": entry.get("L3Data", {}).get("reactivePower"),
                        "L3_cosPhi": entry.get("L3Data", {}).get("cosPhi"),
                        "vL1To2": entry.get("vL1To2"),
                        "vL2To3": entry.get("vL2To3"),
                        "vL3To1": entry.get("vL3To1")
                    }
                    all_data.append(flattened)

        # Save inverter data to CSV
        columns = [
            "date", "totalActivePower", "dcVoltage", "groundFaultResistance", "powerLimit",
            "totalEnergy", "temperature", "inverterMode", "operationMode",
            "L1_acCurrent", "L1_acVoltage", "L1_acFrequency", "L1_apparentPower",
            "L1_activePower", "L1_reactivePower", "L1_cosPhi",
            "L2_acCurrent", "L2_acVoltage", "L2_acFrequency", "L2_apparentPower",
            "L2_activePower", "L2_reactivePower", "L2_cosPhi",
            "L3_acCurrent", "L3_acVoltage", "L3_acFrequency", "L3_apparentPower",
            "L3_activePower", "L3_reactivePower", "L3_cosPhi",
            "vL1To2", "vL2To3", "vL3To1"
        ]
        filename = os.path.join(output_dir, f"inverter_{inverter_name}_{serial_number}.csv")
        save_to_csv(all_data, filename, columns)

if __name__ == "__main__":
    main()

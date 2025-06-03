import sys, csv, os, time, hashlib, requests, pandas as pd
import logging, unicodedata
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from tenacity import retry, stop_after_attempt, wait_fixed
import psycopg2
from psycopg2.extras import execute_batch
from psycopg2.pool import ThreadedConnectionPool
from redis import Redis
from prometheus_client import Counter, Gauge, start_http_server
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

# ─── Configuration ───────────────────────────────────────────────────────────
load_dotenv()
COMPANY_KEY = os.getenv("SHINE_KEY")
API_BASE = os.getenv("SHINE_API")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not all([COMPANY_KEY, API_BASE, DATABASE_URL, JWT_SECRET_KEY]):
    print("❌ Missing SHINE_KEY, SHINE_API, DATABASE_URL, or JWT_SECRET_KEY")
    sys.exit(1)

# ─── Logging Setup ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("ingestion.log"),
        logging.StreamHandler()
    ]
)

# ─── Prometheus Metrics ──────────────────────────────────────────────────────
fetch_success = Counter("fetch_rows_total", "Successful data fetches")
fetch_errors = Counter("fetch_errors_total", "Failed data fetches")
ingest_success = Counter("ingest_readings_total", "Successful readings ingested")
ingest_errors = Counter("ingest_errors_total", "Failed readings ingestion")
api_latency = Gauge("api_latency_seconds", "API request latency")

# ─── Database and Cache Setup ────────────────────────────────────────────────
pool = ThreadedConnectionPool(1, 20, dsn=DATABASE_URL)
redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# ─── Flask Setup ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)

# ─── Utility Functions ───────────────────────────────────────────────────────
def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).strip()

def sha1_lowercase(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_token(usr, pwd):
    salt = str(int(time.time() * 1000))
    pwd_sha = sha1_lowercase(pwd)
    safe_usr = quote_plus(normalize(usr))
    safe_companykey = quote_plus(normalize(COMPANY_KEY))
    action = f"&action=auth&usr={safe_usr}&company-key={safe_companykey}"
    sign = sha1_lowercase(salt + pwd_sha + action)
    url = f"{API_BASE}?sign={sign}&salt={salt}{action}"
    start_time = time.time()
    resp = requests.get(url).json()
    api_latency.set(time.time() - start_time)
    if resp.get("err") == 0:
        return resp["dat"]["token"], resp["dat"]["secret"]
    raise RuntimeError(f"Auth failed for {usr}: {resp.get('desc')}")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def call_api(token, secret, action_params: str):
    salt = str(int(time.time() * 1000))
    action = f"&{action_params}"
    sign = sha1_lowercase(salt + secret + token + action)
    url = f"{API_BASE}?sign={sign}&salt={salt}&token={token}{action}"
    start_time = time.time()
    resp = requests.get(url).json()
    api_latency.set(time.time() - start_time)
    if resp.get("err") != 0:
        raise RuntimeError(f"API error: {resp.get('desc')}")
    return resp

def get_plants(token, secret):
    try:
        resp = call_api(token, secret, "action=queryPlants&pagesize=50")
        if resp.get("err") == 0 and isinstance(resp.get("dat"), dict):
            return [p["pid"] for p in resp["dat"].get("plant", [])]
        return []
    except Exception as e:
        logging.error(f"Failed to get plants: {e}")
        return []

def get_collectors_for_plant(token, secret, plantid):
    try:
        resp = call_api(token, secret, f"action=queryPlantDeviceView&plantid={plantid}")
        if resp.get("err") != 0:
            return []
        raw = resp.get("dat", None)
        coll_list = raw.get("collector", []) if isinstance(raw, dict) else (raw if isinstance(raw, list) else [])
        devices = []
        for coll in coll_list:
            pn = coll.get("pn", "")
            for dev in coll.get("device", []):
                devices.append({
                    "pn": pn,
                    "devcode": str(dev.get("devcode", "")),
                    "devaddr": str(dev.get("devaddr", "")),
                    "sn": dev.get("sn", "")
                })
        return devices
    except Exception as e:
        logging.error(f"Failed to get devices for plant {plantid}: {e}")
        return []

def is_device_online(token, secret, device):
    try:
        salt = str(int(time.time() * 1000))
        param = quote_plus(f"{device['pn']},{device['devcode']},{device['devaddr']},{device['sn']}")
        action = f"&action=queryDeviceStatus&device={param}"
        sign = sha1_lowercase(salt + secret + token + action)
        url = f"{API_BASE}?sign={sign}&salt={salt}&token={token}{action}"
        resp = requests.get(url).json()
        return resp.get("err") == 0 and any(d.get("status") == 0 for d in resp["dat"].get("device", []))
    except Exception as e:
        logging.error(f"Device status check failed for {device['sn']}: {e}")
        return False

def fetch_rows(token, secret, device, start_date=None, end_date=None):
    try:
        start_date = start_date or datetime.now().strftime("%Y-%m-%d")
        end_date = end_date or start_date
        dates = pd.date_range(start_date, end_date).strftime("%Y-%m-%d").tolist()
        all_rows = []
        titles = None
        for date in dates:
            salt = str(int(time.time() * 1000))
            params = {
                "action": "queryDeviceDataOneDay",
                "i18n": "en_US",
                "pn": device["pn"],
                "devcode": device["devcode"],
                "devaddr": device["devaddr"],
                "sn": device["sn"],
                "date": date
            }
            action = "&" + "&".join(f"{k}={quote_plus(v)}" for k, v in params.items())
            sign = sha1_lowercase(salt + secret + token + action)
            url = f"{API_BASE}?sign={sign}&salt={salt}&token={token}{action}"
            data = requests.get(url).json()
            if data.get("err") == 0 and "row" in data["dat"]:
                if not titles:
                    titles = [t["title"] + (f" ({t['unit']})" if t.get("unit") else "") for t in data["dat"]["title"]]
                all_rows.extend([row["field"] for row in data["dat"]["row"]])
        if all_rows:
            fetch_success.inc()
        else:
            fetch_errors.inc()
        return titles, all_rows
    except Exception as e:
        fetch_errors.inc()
        logging.error(f"Fetch failed for {device['sn']}: {e}")
        return None, None

# ─── TimescaleDB Functions ───────────────────────────────────────────────────
def get_or_create_parameter(device_id, param_name, unit=None):
    param_key = f"param:{device_id}:{param_name}"
    param_id = redis_client.get(param_key)
    if param_id:
        return int(param_id)
    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM parameters WHERE device_id = %s AND name = %s", (device_id, param_name))
            result = cursor.fetchone()
            if result:
                param_id = result[0]
            else:
                cursor.execute("INSERT INTO parameters (device_id, name, unit) VALUES (%s, %s, %s) RETURNING id", (device_id, param_name, unit))
                param_id = cursor.fetchone()[0]
                conn.commit()
            redis_client.setex(param_key, 86400, param_id)
            return param_id
    except Exception as e:
        logging.error(f"Parameter creation failed for {param_name}: {e}")
        return None
    finally:
        pool.putconn(conn)

def ingest_to_timescaledb(user_id, device_sn, titles, rows):
    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM devices WHERE serial_number = %s", (device_sn,))
            device_id = cursor.fetchone()
            if not device_id:
                logging.error(f"Device {device_sn} not found")
                return
            device_id = device_id[0]
            readings = []
            for row in rows:
                timestamp = datetime.now()  # Replace with row timestamp if available
                for title, value in zip(titles, row):
                    try:
                        value = float(value) if value else None
                        if value is None:
                            continue
                        param_name = title.lower().replace(" ", "_").split("(")[0].strip()
                        unit = title.split("(")[1].replace(")", "") if "(" in title else None
                        param_id = get_or_create_parameter(device_id, param_name, unit)
                        if param_id:
                            readings.append((device_id, param_id, timestamp, value))
                    except ValueError:
                        logging.warning(f"Invalid value for {title}: {value}")
                if len(readings) >= 5000:
                    execute_batch(cursor, "INSERT INTO readings (device_id, parameter_id, timestamp, value) VALUES (%s, %s, %s, %s)", readings)
                    conn.commit()
                    ingest_success.inc(len(readings))
                    readings = []
            if readings:
                execute_batch(cursor, "INSERT INTO readings (device_id, parameter_id, timestamp, value) VALUES (%s, %s, %s, %s)", readings)
                conn.commit()
                ingest_success.inc(len(readings))
    except Exception as e:
        ingest_errors.inc()
        conn.rollback()
        logging.error(f"Ingestion failed for {device_sn}: {e}")
    finally:
        pool.putconn(conn)

def enable_compression():
    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE readings SET (timescaledb.compress, timescaledb.compress_segmentby = 'device_id');")
            cursor.execute("SELECT add_compression_policy('readings', INTERVAL '7 days');")
            conn.commit()
            logging.info("Compression enabled for readings table")
    except Exception as e:
        logging.error(f"Compression setup failed: {e}")
    finally:
        pool.putconn(conn)

# ─── Main Logic ──────────────────────────────────────────────────────────────
def fetch_device_data(token, secret, device):
    if is_device_online(token, secret, device):
        titles, rows = fetch_rows(token, secret, device)
        return device["sn"], titles, rows
    return device["sn"], None, None

def main(csv_path, start_date=None, end_date=None):
    all_records = []
    columns = None
    enable_compression()  # Ensure compression is set

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

        for rec in reader:
            usr = rec.get("usr", "").strip()
            pwd = rec.get("pwd", "").strip()
            if not usr or not pwd:
                continue

            logging.info(f"Authenticating {usr}...")
            try:
                token, secret = get_token(usr, pwd)
                plant_ids = get_plants(token, secret)
                if not plant_ids:
                    logging.warning(f"No plants for {usr}")
                    continue

                for pid in plant_ids:
                    devices = get_collectors_for_plant(token, secret, pid)
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        results = executor.map(lambda d: fetch_device_data(token, secret, d), devices)
                        for device_sn, titles, rows in results:
                            if not rows:
                                logging.warning(f"No data for device {device_sn}")
                                continue
                            if columns is None:
                                columns = ["usr", "device_sn"] + titles
                            for row in rows:
                                all_records.append([usr, device_sn] + row)
                            ingest_to_timescaledb(usr, device_sn, titles, rows)
            except Exception as e:
                logging.error(f"Error for {usr}: {e}")

    if all_records:
        df = pd.DataFrame(all_records, columns=columns)
        out = f"all_data_{datetime.now():%Y%m%d_%H%M%S}.csv"
        df.to_csv(out, index=False)
        logging.info(f"Wrote {len(all_records)} rows to {out}")

# ─── Flask Endpoints ─────────────────────────────────────────────────────────
@app.route("/api/fetch/<user_id>", methods=["GET"])
@jwt_required()
def fetch_user_data(user_id):
    if get_jwt_identity() != user_id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    with open("accounts.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for rec in reader:
            if rec.get("usr") == user_id:
                try:
                    token, secret = get_token(rec["usr"], rec["pwd"])
                    plant_ids = get_plants(token, secret)
                    for pid in plant_ids:
                        devices = get_collectors_for_plant(token, secret, pid)
                        for device in devices:
                            titles, rows = fetch_rows(token, secret, device, start_date, end_date)
                            if rows:
                                ingest_to_timescaledb(user_id, device["sn"], titles, rows)
                    return jsonify({"status": "success", "user": user_id})
                except Exception as e:
                    logging.error(f"Fetch failed for {user_id}: {e}")
                    return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "User not found"}), 404

# ─── Scheduler Setup ─────────────────────────────────────────────────────────
def scheduled_fetch():
    logging.info("Starting scheduled data fetch")
    main("accounts.csv")

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_fetch, "interval", minutes=5)  # Real-time
scheduler.add_job(scheduled_fetch, "cron", hour=0)  # Daily
scheduler.start()

# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    start_http_server(8000)  # Prometheus metrics
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        scheduler.shutdown()
        pool.closeall()
        logging.info("Shutdown complete")
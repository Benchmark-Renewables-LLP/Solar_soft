import os
import sys
import time
import hashlib
import requests
from dotenv import load_dotenv
from urllib.parse import quote_plus
import unicodedata

# Load env vars
load_dotenv()

USR = os.getenv("SHINE_USR")
PWD = os.getenv("SHINE_PWD")
COMPANY_KEY = os.getenv("SHINE_KEY")
API_BASE = os.getenv("SHINE_API")

if not all([USR, PWD, COMPANY_KEY, API_BASE]):
    print("❌ Missing one or more required environment variables")
    sys.exit(1)

def normalize(text):
    return unicodedata.normalize("NFKC", text).strip()

def sha1_lowercase(s):
    return hashlib.sha1(s.encode()).hexdigest()

def get_token():
    salt = str(int(time.time() * 1000))
    pwd_sha = sha1_lowercase(PWD)
    action = f"&action=auth&usr={quote_plus(normalize(USR))}&company-key={quote_plus(COMPANY_KEY)}"
    sign = sha1_lowercase(salt + pwd_sha + action)
    url = f"{API_BASE}?sign={sign}&salt={salt}{action}"
    resp = requests.get(url).json()
    if resp.get("err") == 0:
        print(f"✅ Auth success for user {USR}")
        return resp["dat"]["token"], resp["dat"]["secret"]
    else:
        print(f"❌ Auth failed: {resp.get('desc')}")
        sys.exit(1)

def get_plants(token, secret):
    salt = str(int(time.time() * 1000))
    action = "&action=queryPlants&pagesize=5"
    sign = sha1_lowercase(salt + secret + token + action)
    url = f"{API_BASE}?sign={sign}&salt={salt}&token={token}{action}"
    resp = requests.get(url).json()
    if resp.get("err") == 0:
        plants = resp.get("dat", {}).get("plant", [])
        print(f"🌱 Found {len(plants)} plants:")
        for p in plants:
            print(f"  - {p.get('name', '')} (ID: {p.get('pid')})")
    else:
        print(f"❌ Failed to fetch plants: {resp.get('desc')}")

def main():
    token, secret = get_token()
    get_plants(token, secret)

if __name__ == "__main__":
    main()

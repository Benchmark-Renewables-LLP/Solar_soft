import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Shinemonitor API credentials (fallback if not using users.csv)
SHINEMONITOR_USERNAME = os.getenv("SHINEMONITOR_USERNAME")
SHINEMONITOR_PASSWORD = os.getenv("SHINEMONITOR_PASSWORD")
COMPANY_KEY = os.getenv("COMPANY_KEY")
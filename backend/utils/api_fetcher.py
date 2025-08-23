from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.config.settings import settings
from backend.utils.api_clients.solarman_api import SolarmanAPI
from backend.utils.api_clients.shinemonitor_api import ShinemonitorAPI
from backend.utils.api_clients.soliscloud_api import SolisCloudAPI
from backend.services.etl_service import normalize_data_entry, insert_data_to_db
import logging
from datetime import datetime, timedelta

engine = create_engine(settings.POSTGRES_URL)
Session = sessionmaker(bind=engine)
logger = logging.getLogger(__name__)

def get_client(api_provider, credential):
    if api_provider == 'solarman':
        return SolarmanAPI(credential['email'], credential['password_sha256'], credential['api_key'], credential['api_secret'])
    elif api_provider == 'shinemonitor':
        return ShinemonitorAPI(settings.COMPANY_KEY)
    elif api_provider == 'soliscloud':
        return SolisCloudAPI(credential['api_key'], credential['api_secret'])
    raise ValueError(f"Unknown API provider: {api_provider}")

def fetch_for_all_panels(historical=False):  # Called from Airflow
    with Session() as session:
        credentials = session.execute(text("SELECT * FROM api_credentials")).fetchall()
        for cred_row in credentials:
            credential = dict(cred_row)
            api_provider = credential['api_provider']
            client = get_client(api_provider, credential)
            plants = client.get_plant_list(credential['user_id'], credential['username'], credential['password']) if api_provider == 'solarman' else ...  # Adapt per client
            for plant in plants:
                devices = client.get_all_devices(credential['user_id'], credential['username'], credential['password'], plant['plant_id']) if api_provider == 'solarman' else ...  # Adapt
                for device in devices:
                    if historical:
                        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')  # Example: Last week
                        data = client.get_historical_data(credential['user_id'], credential['username'], credential['password'], device, start_date, datetime.now().strftime('%Y-%m-%d'))
                    else:
                        data = client.get_realtime_data(credential['user_id'], credential['username'], credential['password'], device)
                    normalized = [normalize_data_entry(entry, api_provider) for entry in data]
                    insert_data_to_db(session, normalized, device['deviceSn'], credential['customer_id'], api_provider, not historical)
            session.commit()
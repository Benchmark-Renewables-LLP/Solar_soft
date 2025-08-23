from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from .db import get_db_connection, close_db_connection, DBConnection
from .utils import validate_email, validate_whatsapp_number, validate_customer_id, hash_password, verify_password, create_jwt_token
from datetime import datetime
from pytz import timezone
from fetch_historic_data import fetch_historic_data
import logging
import os

# Logging setup
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'auth')
os.makedirs(log_dir, exist_ok=True)
log_date = datetime.now(timezone('Asia/Kolkata')).strftime('%Y%m%d')
log_file = os.path.join(log_dir, f'auth_{log_date}.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class UserRegister(BaseModel):
    username: str
    fullname: str
    password: str
    confirmPassword: str
    panelBrand: str
    panelCapacity: float
    panelType: str
    inverterBrand: str
    inverterCapacity: float
    email: str
    whatsappNumber: str | None = None
    address: str
    isInstaller: bool = False

class UserLogin(BaseModel):
    username: str
    password: str
    isInstaller: bool = False

# Dependency to manage database connection
def get_db():
    db = get_db_connection()
    try:
        yield db
    finally:
        close_db_connection(db)

# Registration endpoint
@router.post("/register")
async def register(user: UserRegister, db: DBConnection = Depends(get_db)):
    try:
        # Validate inputs
        if user.password != user.confirmPassword:
            logger.error("Registration failed: Passwords do not match")
            raise HTTPException(status_code=400, detail="Passwords do not match")

        email_valid, email_error = validate_email(user.email)
        if not email_valid:
            logger.error(f"Registration failed: {email_error}")
            raise HTTPException(status_code=400, detail=email_error)

        whatsapp_valid, whatsapp_error = validate_whatsapp_number(user.whatsappNumber)
        if not whatsapp_valid:
            logger.error(f"Registration failed: {whatsapp_error}")
            raise HTTPException(status_code=400, detail=whatsapp_error)

        # Generate customer_id
        customer_id = re.sub(r'[^a-zA-Z0-9_]', '_', user.username.lower())
        customer_valid, customer_error = validate_customer_id(customer_id)
        if not customer_valid:
            logger.error(f"Registration failed: {customer_error}")
            raise HTTPException(status_code=400, detail=customer_error)

        # Check for duplicates
        with db.cursor() as cur:
            cur.execute("SELECT 1 FROM customers WHERE username = %s", (user.username,))
            if cur.fetchone():
                logger.error(f"Registration failed: Username {user.username} already exists")
                raise HTTPException(status_code=400, detail="Username already exists")
            cur.execute("SELECT 1 FROM customers WHERE email = %s", (user.email,))
            if cur.fetchone():
                logger.error(f"Registration failed: Email {user.email} already exists")
                raise HTTPException(status_code=400, detail="Email already exists")

        # Hash password
        hashed_password = hash_password(user.password)

        # Insert customer into TimescaleDB
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO customers (
                    customer_id, customer_name, username, password, email, phone, address, is_installer, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                customer_id, user.fullname, user.username, hashed_password, user.email,
                user.whatsappNumber, user.address, user.isInstaller,
                datetime.now(timezone('Asia/Kolkata')), datetime.now(timezone('Asia/Kolkata'))
            ))
        db.commit()
        logger.info(f"Customer registered: {customer_id}, is_installer: {user.isInstaller}")

        # Insert plant and device
        plant_id = f"p{db.cursor().execute('SELECT COUNT(*) FROM plants') + 1:06d}"
        device_id = f"d{db.cursor().execute('SELECT COUNT(*) FROM devices') + 1:06d}"
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO plants (
                    plant_id, customer_id, plant_name, capacity, install_date, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                plant_id, customer_id, f"{user.fullname}'s Plant", user.panelCapacity,
                datetime.now(timezone('Asia/Kolkata')).strftime('%Y-%m-%d'),
                datetime.now(timezone('Asia/Kolkata')), datetime.now(timezone('Asia/Kolkata'))
            ))
            cur.execute("""
                INSERT INTO devices (
                    device_sn, plant_id, inverter_model, panel_model, panel_type, pv_count, string_count,
                    first_install_date, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                device_id, plant_id, user.inverterBrand, user.panelBrand, user.panelType, 0, 0,
                datetime.now(timezone('Asia/Kolkata')).strftime('%Y-%m-%d'),
                datetime.now(timezone('Asia/Kolkata')), datetime.now(timezone('Asia/Kolkata'))
            ))
        db.commit()
        logger.info(f"Plant {plant_id} and device {device_id} created for customer {customer_id}")

        # Trigger historical data fetch
        try:
            fetch_historic_data()
            logger.info(f"Historical data fetch triggered for customer {customer_id}")
        except Exception as e:
            logger.error(f"Failed to trigger historical data fetch: {e}")

        # Generate JWT token
        token = create_jwt_token(customer_id, user.isInstaller)
        return {"token": token}
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

# Login endpoint
@router.post("/login")
async def login(user: UserLogin, db: DBConnection = Depends(get_db)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT password, is_installer FROM customers WHERE username = %s", (user.username,))
            db_user = cur.fetchone()
            if not db_user or not verify_password(user.password, db_user[0]) or db_user[1] != user.isInstaller:
                logger.error(f"Login failed: Invalid credentials for {user.username}, is_installer={user.isInstaller}")
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # Generate JWT token
            token = create_jwt_token(user.username, user.isInstaller)
            logger.info(f"User logged in: {user.username}, is_installer: {user.isInstaller}")
            return {"token": token}
    except Exception as e:
        logger.error(f"Login error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

# Flask Backend Implementation Guide for Solar PV Dashboard

## Prerequisites

### Required Python Packages
```bash
pip install flask flask-cors flask-jwt-extended python-dotenv
pip install psycopg2-binary sqlalchemy pymongo
pip install google-auth google-auth-oauthlib google-auth-httplib2
pip install bcrypt python-jose[cryptography]
pip install flask-migrate flask-sqlalchemy
```

### Environment Variables (.env)
```env
# Database Configuration
TIMESCALE_DB_URL=postgresql://username:password@localhost:5432/solar_timeseries
MONGODB_URI=mongodb://localhost:27017/solar_pv_dashboard

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ACCESS_TOKEN_EXPIRES=7200  # 2 hours in seconds

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
CORS_ORIGINS=http://localhost:5173,https://your-frontend-domain.com

# Optional
BCRYPT_LOG_ROUNDS=12
```

## Step 1: Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── plant.py
│   │   ├── device.py
│   │   └── timeseries.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── google_auth.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── plants.py
│   │   ├── devices.py
│   │   └── timeseries.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   └── error_handlers.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── mongodb.py
│   │   └── timescale.py
│   └── utils/
│       ├── __init__.py
│       ├── decorators.py
│       └── helpers.py
├── migrations/
├── requirements.txt
├── run.py
└── .env
```

## Step 2: Core Configuration (app/config.py)

```python
import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 7200)))
    
    # Database URLs
    TIMESCALE_DB_URL = os.getenv('TIMESCALE_DB_URL')
    MONGODB_URI = os.getenv('MONGODB_URI')
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

## Step 3: Database Models

### MongoDB Models (app/models/user.py)
```python
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime

class User:
    def __init__(self, db):
        self.collection = db.users
    
    def create_user(self, name, email, password, google_id=None):
        user_data = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password) if password else None,
            'google_id': google_id,
            'role': 'user',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def find_by_email(self, email):
        return self.collection.find_one({'email': email})
    
    def find_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def verify_password(self, user, password):
        if not user.get('password'):
            return False
        return check_password_hash(user['password'], password)
```

### TimeScale DB Models (app/models/timeseries.py)
```python
from sqlalchemy import create_engine, Column, DateTime, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class DeviceMetrics(Base):
    __tablename__ = 'device_metrics'
    
    time = Column(DateTime, primary_key=True)
    device_id = Column(String, primary_key=True)
    metric_type = Column(String, primary_key=True)
    metric_name = Column(String, primary_key=True)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    quality = Column(Integer, default=100)

class DeviceEvents(Base):
    __tablename__ = 'device_events'
    
    time = Column(DateTime, primary_key=True)
    device_id = Column(String, primary_key=True)
    event_type = Column(String, primary_key=True)
    event_code = Column(String, nullable=False)
    message = Column(String)
    severity = Column(Integer, nullable=False)
    acknowledged = Column(Integer, default=0)
```

## Step 4: Authentication Routes (app/auth/routes.py)

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.auth.google_auth import verify_google_token
from app.database.mongodb import get_mongo_db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    db = get_mongo_db()
    user_model = User(db)
    user = user_model.find_by_email(email)
    
    if user and user_model.verify_password(user, password):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            'token': access_token,
            'user': {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email']
            }
        }), 200
    
    return jsonify({'detail': 'Invalid email or password'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    db = get_mongo_db()
    user_model = User(db)
    
    if user_model.find_by_email(email):
        return jsonify({'detail': 'Email already exists'}), 400
    
    user_id = user_model.create_user(name, email, password)
    user = user_model.find_by_id(user_id)
    
    access_token = create_access_token(identity=user_id)
    return jsonify({
        'token': access_token,
        'user': {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email']
        }
    }), 201

@auth_bp.route('/google', methods=['POST'])
def google_login():
    data = request.get_json()
    google_token = data.get('token')
    
    user_info = verify_google_token(google_token)
    if not user_info:
        return jsonify({'detail': 'Invalid Google token'}), 401
    
    db = get_mongo_db()
    user_model = User(db)
    user = user_model.find_by_email(user_info['email'])
    
    if not user:
        # Create new user from Google
        user_id = user_model.create_user(
            name=user_info['name'],
            email=user_info['email'],
            password=None,
            google_id=user_info['sub']
        )
        user = user_model.find_by_id(user_id)
    
    access_token = create_access_token(identity=str(user['_id']))
    return jsonify({
        'token': access_token,
        'user': {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email']
        }
    }), 200
```

## Step 5: Google OAuth Helper (app/auth/google_auth.py)

```python
from google.auth.transport import requests
from google.oauth2 import id_token
from app.config import Config

def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            Config.GOOGLE_CLIENT_ID
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
            
        return idinfo
    except ValueError:
        return None
```

## Step 6: Middleware (app/middleware/auth_middleware.py)

```python
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.database.mongodb import get_mongo_db

def auth_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        current_user_id = get_jwt_identity()
        db = get_mongo_db()
        user_model = User(db)
        user = user_model.find_by_id(current_user_id)
        
        if not user or not user.get('is_active'):
            return jsonify({'detail': 'User not found or inactive'}), 401
            
        return f(current_user=user, *args, **kwargs)
    return decorated
```

## Step 7: Main Application (app/__init__.py)

```python
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import DevelopmentConfig, ProductionConfig
from app.auth.routes import auth_bp
from app.api.plants import plants_bp
from app.api.devices import devices_bp
from app.api.timeseries import timeseries_bp
from app.middleware.error_handlers import register_error_handlers
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    if os.getenv('FLASK_ENV') == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # Extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    JWTManager(app)
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(plants_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(timeseries_bp)
    
    # Error Handlers
    register_error_handlers(app)
    
    return app
```

## Step 8: Database Connections

### MongoDB Connection (app/database/mongodb.py)
```python
from pymongo import MongoClient
from app.config import Config

_mongo_client = None
_mongo_db = None

def init_mongodb():
    global _mongo_client, _mongo_db
    _mongo_client = MongoClient(Config.MONGODB_URI)
    _mongo_db = _mongo_client.solar_pv_dashboard

def get_mongo_db():
    if _mongo_db is None:
        init_mongodb()
    return _mongo_db
```

### TimeScale DB Connection (app/database/timescale.py)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Config
from app.models.timeseries import Base

engine = create_engine(Config.TIMESCALE_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_timescale_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_timescale():
    Base.metadata.create_all(bind=engine)
```

## Step 9: Run Script (run.py)

```python
from app import create_app
from app.database.mongodb import init_mongodb
from app.database.timescale import init_timescale

app = create_app()

if __name__ == '__main__':
    init_mongodb()
    init_timescale()
    app.run(host='0.0.0.0', port=8000, debug=True)
```

## API Endpoints Summary

### Authentication Endpoints
- `POST /api/auth/login` - Email/password login
- `POST /api/auth/register` - User registration
- `POST /api/auth/google` - Google OAuth login

### Plants Endpoints
- `GET /api/plants` - Get all plants for user
- `GET /api/plants/{plantId}` - Get specific plant details

### Devices Endpoints
- `GET /api/devices` - Get all devices for user
- `GET /api/devices/{deviceId}` - Get specific device details
- `GET /api/plants/{plantId}/devices` - Get devices for specific plant

### Time-Series Endpoints
- `GET /api/devices/{deviceId}/timeseries` - Get time-series data
- `POST /api/devices/{deviceId}/timeseries/batch` - Get multiple metrics

## Google OAuth Setup Instructions

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs: `http://localhost:5173` (for development)
6. Copy Client ID and Client Secret to your .env file

## Database Setup Instructions

### TimeScale DB Setup
```sql
-- Create database
CREATE DATABASE solar_timeseries;

-- Connect to database and create extension
\c solar_timeseries;
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Tables will be created automatically by SQLAlchemy
-- But you can create hypertables manually:
SELECT create_hypertable('device_metrics', 'time');
SELECT create_hypertable('device_events', 'time');
```

### MongoDB Setup
```bash
# MongoDB collections will be created automatically
# No additional setup required
```

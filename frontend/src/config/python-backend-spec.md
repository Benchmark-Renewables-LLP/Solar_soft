
# Python Backend API Specification

This document specifies the exact API endpoints and data formats your Python backend needs to implement to work with this frontend.

## Environment Variables

Your Python backend should read:
```
TIMESCALE_DB_URL=postgresql://username:password@localhost:5432/solar_timeseries
MONGODB_URI=mongodb://localhost:27017/solar_pv_dashboard
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRES_IN=7d
```

## Required API Endpoints

### 1. Authentication Endpoints

#### POST /api/auth/login
```json
// Request Body
{
  "username": "demo",
  "password": "demo123",
  "userType": "customer" // or "installer"
}

// Response (200 OK)
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "demo",
    "name": "John Smith",
    "email": "user@example.com",
    "userType": "customer",
    "profile": {
      // Customer-specific fields
      "installationId": "INST-12345",
      "address": "123 Solar Street, CA"
    }
  }
}

// Response for Installer (200 OK)
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439012",
    "username": "installer1",
    "name": "Solar Install Co",
    "email": "installer@solarco.com",
    "userType": "installer",
    "profile": {
      // Installer-specific fields
      "companyName": "Solar Install Co",
      "licenseNumber": "LIC-789",
      "phoneNumber": "+1-555-0123"
    }
  }
}

// Error Response (401 Unauthorized)
{
  "detail": "Invalid username or password"
}
```

#### POST /api/auth/register
```json
// Request Body for Customer
{
  "name": "John Smith",
  "email": "user@example.com",
  "password": "password123",
  "userType": "customer",
  "installationId": "INST-12345",
  "address": "123 Solar Street, CA"
}

// Request Body for Installer
{
  "name": "Jane Installer",
  "email": "installer@solarco.com",
  "password": "password123",
  "userType": "installer",
  "companyName": "Solar Install Co",
  "licenseNumber": "LIC-789",
  "phoneNumber": "+1-555-0123"
}

// Response (201 Created)
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "generated-username", // auto-generated from email
    "name": "John Smith",
    "email": "user@example.com",
    "userType": "customer",
    "profile": {
      "installationId": "INST-12345",
      "address": "123 Solar Street, CA"
    }
  }
}

// Error Response (400 Bad Request)
{
  "detail": "Email already exists"
}
```

#### POST /api/auth/google
```json
// Request Body
{
  "token": "google-oauth-token-from-frontend",
  "userType": "customer" // or "installer"
}

// Response (200 OK)
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "google-user-123",
    "name": "John Smith",
    "email": "user@example.com",
    "userType": "customer",
    "profile": {}
  }
}
```

### 2. User Profile Endpoints

#### GET /api/users/profile
```json
// Headers: Authorization: Bearer <token>
// Response (200 OK)
{
  "id": "507f1f77bcf86cd799439011",
  "username": "demo",
  "name": "John Smith",
  "email": "user@example.com",
  "userType": "customer",
  "profile": {
    "installationId": "INST-12345",
    "address": "123 Solar Street, CA"
  },
  "createdAt": "2023-06-15T00:00:00Z",
  "lastLogin": "2024-01-01T12:00:00Z"
}
```

#### PUT /api/users/profile
```json
// Headers: Authorization: Bearer <token>
// Request Body
{
  "name": "John Updated Smith",
  "profile": {
    "installationId": "INST-54321",
    "address": "456 New Solar Avenue, CA"
  }
}

// Response (200 OK)
{
  "id": "507f1f77bcf86cd799439011",
  "username": "demo",
  "name": "John Updated Smith",
  "email": "user@example.com",
  "userType": "customer",
  "profile": {
    "installationId": "INST-54321",
    "address": "456 New Solar Avenue, CA"
  }
}
```

### 3. Plants Endpoints

#### GET /api/plants
```json
// Headers: Authorization: Bearer <token>
// Note: Customers see only their plants, Installers see all plants they manage
// Response (200 OK)
[
  {
    "id": "507f1f77bcf86cd799439011",
    "name": "Solar Farm Alpha",
    "location": "California, USA",
    "totalCapacity": 500,
    "currentGeneration": 387.5,
    "efficiency": 92.3,
    "deviceCount": 8,
    "status": "online",
    "lastUpdate": "2024-01-01T12:00:00Z",
    "ownerId": "customer-123", // Customer who owns this plant
    "installerId": "installer-456" // Installer who manages this plant
  }
]
```

#### GET /api/plants/{plantId}
```json
// Response (200 OK)
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Solar Farm Alpha",
  "location": "California, USA",
  "coordinates": {
    "lat": 37.7749,
    "lng": -122.4194
  },
  "totalCapacity": 500,
  "currentGeneration": 387.5,
  "efficiency": 92.3,
  "deviceCount": 8,
  "status": "online",
  "installationDate": "2023-06-15T00:00:00Z",
  "lastUpdate": "2024-01-01T12:00:00Z",
  "ownerId": "customer-123",
  "installerId": "installer-456"
}
```

### 4. Devices Endpoints

#### GET /api/devices
```json
// Headers: Authorization: Bearer <token>
// Response (200 OK)
[
  {
    "id": "device-123",
    "plantId": "507f1f77bcf86cd799439011",
    "name": "Inverter A1",
    "type": "inverter",
    "status": "online",
    "currentOutput": 45.2,
    "efficiency": 94.1,
    "lastUpdate": "2024-01-01T12:00:00Z"
  }
]
```

#### GET /api/plants/{plantId}/devices
```json
// Same format as GET /api/devices but filtered by plantId
```

#### GET /api/devices/{deviceId}
```json
// Response (200 OK)
{
  "id": "device-123",
  "plantId": "507f1f77bcf86cd799439011",
  "name": "Inverter A1",
  "type": "inverter",
  "model": "SolarEdge SE7600A",
  "serialNumber": "SE7600A-12345",
  "capacity": 7.6,
  "status": "online",
  "currentOutput": 45.2,
  "efficiency": 94.1,
  "firmware": "1.2.3",
  "lastCommunication": "2024-01-01T12:00:00Z",
  "lastUpdate": "2024-01-01T12:00:00Z"
}
```

### 5. Time-Series Data Endpoints

#### GET /api/devices/{deviceId}/timeseries
```
Query Parameters:
- metric: string (e.g., "panel_voltages", "input_currents", "power_generation")
- timeRange: string ("1h", "24h", "7d", "30d")
- startTime: string (optional, ISO format)
- endTime: string (optional, ISO format)
```

```json
// Response (200 OK)
{
  "deviceId": "device-123",
  "metric": "panel_voltages",
  "timeRange": "24h",
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "PV1": 245.2,
      "PV2": 243.8,
      "PV3": 246.1,
      "PV4": 244.5
    },
    {
      "timestamp": "2024-01-01T00:15:00Z",
      "PV1": 246.1,
      "PV2": 244.2,
      "PV3": 245.8,
      "PV4": 243.9
    }
  ]
}
```

#### POST /api/devices/{deviceId}/timeseries/batch
```json
// Request Body
{
  "metrics": ["panel_voltages", "input_currents", "power_generation"],
  "timeRange": "24h"
}

// Response (200 OK)
[
  {
    "deviceId": "device-123",
    "metric": "panel_voltages",
    "timeRange": "24h",
    "data": [...]
  },
  {
    "deviceId": "device-123",
    "metric": "input_currents",
    "timeRange": "24h",
    "data": [...]
  }
]
```

## Database Schema Considerations

### User Collection (MongoDB)
```json
{
  "_id": "ObjectId",
  "username": "string (unique)",
  "email": "string (unique)",
  "name": "string",
  "passwordHash": "string",
  "userType": "customer | installer",
  "profile": {
    // Customer profile
    "installationId": "string",
    "address": "string",
    
    // Installer profile
    "companyName": "string",
    "licenseNumber": "string",
    "phoneNumber": "string"
  },
  "createdAt": "Date",
  "lastLogin": "Date",
  "isActive": "boolean"
}
```

### Plant Collection (MongoDB)
```json
{
  "_id": "ObjectId",
  "name": "string",
  "location": "string",
  "coordinates": {
    "lat": "number",
    "lng": "number"
  },
  "totalCapacity": "number",
  "ownerId": "ObjectId (ref: User)",
  "installerId": "ObjectId (ref: User)",
  "installationDate": "Date",
  "status": "online | offline | maintenance",
  "createdAt": "Date",
  "updatedAt": "Date"
}
```

## Authorization Rules

### Customer Users
- Can only access their own plants and devices
- Cannot create or modify plants
- Can view their profile and update basic info
- Cannot access other customers' data

### Installer Users
- Can access all plants they manage (installerId matches their user ID)
- Can create new plants and assign them to customers
- Can modify plants they manage
- Can view customer profiles for plants they manage
- Cannot access plants managed by other installers

## Error Handling

All error responses should follow this format:
```json
{
  "detail": "Human readable error message",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR" // Optional error code for frontend handling
}
```

Common HTTP status codes:
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid/missing token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 422: Unprocessable Entity (invalid data format)
- 500: Internal Server Error

## CORS Configuration

Your Python backend must allow CORS for the frontend domain:
```python
# FastAPI example
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Framework Recommendations

**FastAPI + SQLAlchemy + Psycopg2 + PyMongo**
- FastAPI for the API framework
- SQLAlchemy for TimeScale DB ORM
- Psycopg2 for PostgreSQL/TimeScale DB connection
- PyMongo for MongoDB operations
- python-jose for JWT handling
- bcrypt for password hashing

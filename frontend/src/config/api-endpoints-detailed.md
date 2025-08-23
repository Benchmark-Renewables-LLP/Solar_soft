
# Detailed API Endpoints Documentation

## Base URL
```
Development: http://localhost:8000/api
Production: https://your-backend-domain.com/api
```

## Authentication Endpoints

### 1. Username/Password Login (Updated)
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "demo",
  "password": "demo123",
  "userType": "customer"
}
```

**Success Response for Customer (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "demo",
    "name": "John Smith",
    "email": "user@example.com",
    "userType": "customer",
    "profile": {
      "installationId": "INST-12345",
      "address": "123 Solar Street, CA"
    }
  }
}
```

**Success Response for Installer (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439012",
    "username": "installer1",
    "name": "Solar Install Co",
    "email": "installer@solarco.com",
    "userType": "installer",
    "profile": {
      "companyName": "Solar Install Co",
      "licenseNumber": "LIC-789",
      "phoneNumber": "+1-555-0123"
    }
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid username or password"
}
```

### 2. User Registration (Updated)
```http
POST /api/auth/register
Content-Type: application/json

// Customer Registration
{
  "name": "John Smith",
  "email": "user@example.com",
  "password": "password123",
  "userType": "customer",
  "installationId": "INST-12345",
  "address": "123 Solar Street, CA"
}

// Installer Registration
{
  "name": "Jane Installer",
  "email": "installer@solarco.com",
  "password": "password123",
  "userType": "installer",
  "companyName": "Solar Install Co",
  "licenseNumber": "LIC-789",
  "phoneNumber": "+1-555-0123"
}
```

**Success Response (201 Created):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "auto-generated-username",
    "name": "John Smith",
    "email": "user@example.com",
    "userType": "customer",
    "profile": {
      "installationId": "INST-12345",
      "address": "123 Solar Street, CA"
    }
  }
}
```

### 3. Google OAuth Login (Updated)
```http
POST /api/auth/google
Content-Type: application/json

{
  "token": "google-oauth-token-from-frontend",
  "userType": "customer"
}
```

**Success Response (200 OK):**
```json
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

### 4. Get User Profile (New)
```http
GET /api/users/profile
Authorization: Bearer <jwt-token>
```

**Success Response (200 OK):**
```json
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

### 5. Update User Profile (New)
```http
PUT /api/users/profile
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "name": "John Updated Smith",
  "profile": {
    "installationId": "INST-54321",
    "address": "456 New Solar Avenue, CA"
  }
}
```

**Success Response (200 OK):**
```json
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

## Plants Endpoints

### 6. Get All Plants (Updated)
```http
GET /api/plants
Authorization: Bearer <jwt-token>
```

**Success Response (200 OK):**
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "name": "Solar Farm Alpha",
    "location": "California, USA",
    "totalCapacity": 500.0,
    "currentGeneration": 387.5,
    "efficiency": 92.3,
    "deviceCount": 8,
    "status": "online",
    "lastUpdate": "2024-01-01T12:00:00Z",
    "ownerId": "customer-123",
    "installerId": "installer-456"
  }
]
```

### 7. Get Specific Plant (Updated)
```http
GET /api/plants/{plantId}
Authorization: Bearer <jwt-token>
```

**Success Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Solar Farm Alpha",
  "location": "California, USA",
  "coordinates": {
    "lat": 37.7749,
    "lng": -122.4194
  },
  "totalCapacity": 500.0,
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

### 8. Create Plant (New - Installer Only)
```http
POST /api/plants
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "name": "New Solar Installation",
  "location": "Texas, USA",
  "coordinates": {
    "lat": 29.7604,
    "lng": -95.3698
  },
  "totalCapacity": 750.0,
  "ownerId": "customer-123"
}
```

**Success Response (201 Created):**
```json
{
  "id": "507f1f77bcf86cd799439013",
  "name": "New Solar Installation",
  "location": "Texas, USA",
  "coordinates": {
    "lat": 29.7604,
    "lng": -95.3698
  },
  "totalCapacity": 750.0,
  "currentGeneration": 0,
  "efficiency": 0,
  "deviceCount": 0,
  "status": "offline",
  "installationDate": "2024-01-01T00:00:00Z",
  "lastUpdate": "2024-01-01T00:00:00Z",
  "ownerId": "customer-123",
  "installerId": "installer-456"
}
```

## Devices Endpoints

### 9. Get All Devices
```http
GET /api/devices
Authorization: Bearer <jwt-token>
```

**Success Response (200 OK):**
```json
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

### 10. Get Plant Devices
```http
GET /api/plants/{plantId}/devices
Authorization: Bearer <jwt-token>
```

**Success Response (200 OK):**
Same format as GET /api/devices but filtered by plantId

### 11. Get Specific Device
```http
GET /api/devices/{deviceId}
Authorization: Bearer <jwt-token>
```

**Success Response (200 OK):**
```json
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

## Time-Series Data Endpoints

### 12. Get Time-Series Data
```http
GET /api/devices/{deviceId}/timeseries?metric=panel_voltages&timeRange=24h&startTime=2024-01-01T00:00:00Z&endTime=2024-01-02T00:00:00Z
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `metric` (required): `panel_voltages`, `input_currents`, `output_currents`, `power_generation`
- `timeRange` (required): `1h`, `24h`, `7d`, `30d`
- `startTime` (optional): ISO format timestamp
- `endTime` (optional): ISO format timestamp

**Success Response (200 OK):**
```json
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
      "PV4": 244.5,
      "PV5": 245.9,
      "PV6": 243.2,
      "PV7": 246.8,
      "PV8": 244.1,
      "PV9": 245.5,
      "PV10": 243.9
    }
  ]
}
```

### 13. Get Multiple Time-Series Data (Batch)
```http
POST /api/devices/{deviceId}/timeseries/batch
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "metrics": ["panel_voltages", "input_currents", "power_generation"],
  "timeRange": "24h"
}
```

**Success Response (200 OK):**
```json
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
  },
  {
    "deviceId": "device-123",
    "metric": "power_generation",
    "timeRange": "24h",
    "data": [...]
  }
]
```

## Authorization & Permissions

### Customer Users
- **Plants**: Can only view plants where `ownerId` matches their user ID
- **Devices**: Can only view devices from their owned plants
- **Profile**: Can view and update their own profile only
- **Time-series**: Can view data from devices in their owned plants

### Installer Users
- **Plants**: Can view plants where `installerId` matches their user ID
- **Plants**: Can create new plants and assign `ownerId` to customers
- **Plants**: Can update plants they manage
- **Devices**: Can view and manage devices from plants they installed
- **Profile**: Can view and update their own profile
- **Customers**: Can view profiles of customers whose plants they manage
- **Time-series**: Can view data from devices in plants they manage

## Error Responses

All endpoints can return these error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error: missing required field 'userType'",
  "error_code": "VALIDATION_ERROR"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required",
  "error_code": "AUTH_REQUIRED"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions to access this resource",
  "error_code": "INSUFFICIENT_PERMISSIONS"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found",
  "error_code": "NOT_FOUND"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": "Invalid user type. Must be 'customer' or 'installer'",
  "error_code": "INVALID_USER_TYPE"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR"
}
```

## Rate Limiting
- All endpoints are rate-limited to 100 requests per minute per IP
- Authentication endpoints are rate-limited to 10 requests per minute per IP

## CORS Configuration
The backend must allow CORS for these origins:
- `http://localhost:5173` (development)
- `https://your-frontend-domain.com` (production)

## Authentication Flow
1. User logs in via `/api/auth/login` with username/password and userType
2. Backend validates credentials and userType
3. Backend returns JWT token with user info including userType and profile
4. Frontend stores token and includes it in `Authorization: Bearer <token>` header
5. Backend validates token and checks permissions based on userType
6. Token expires after configurable time (default: 7 days)

## Google OAuth Flow
1. Frontend initiates Google OAuth and receives Google token
2. Frontend sends Google token and userType to `/api/auth/google`
3. Backend verifies token with Google
4. Backend creates/finds user with specified userType and returns JWT token
5. Same authentication flow as username/password from this point

## Demo Credentials
The system should support these hardcoded demo accounts:

**Customer Demo Account:**
- Username: `demo`
- Password: `demo123`
- UserType: `customer`

**Installer Demo Account:**
- Username: `admin`
- Password: `admin123`
- UserType: `installer`

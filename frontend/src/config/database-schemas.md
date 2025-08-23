
# Database Schemas for Solar PV Dashboard

## MongoDB Collections (User Authentication & Metadata)

### Users Collection
```json
{
  "_id": "ObjectId",
  "name": "John Smith",
  "email": "john@example.com",
  "password": "bcrypt_hashed_password",
  "role": "user", // "admin", "user", "viewer"
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z",
  "isActive": true
}
```

### Plants Collection
```json
{
  "_id": "ObjectId",
  "userId": "ObjectId", // Reference to Users
  "name": "Solar Farm Alpha",
  "location": "California, USA",
  "coordinates": {
    "lat": 37.7749,
    "lng": -122.4194
  },
  "totalCapacity": 500, // kW
  "installationDate": "2023-06-15T00:00:00Z",
  "status": "online", // "online", "offline", "maintenance"
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### Devices Collection
```json
{
  "_id": "ObjectId",
  "plantId": "ObjectId", // Reference to Plants
  "name": "Inverter A1",
  "type": "inverter", // "inverter", "panel", "meter"
  "model": "SolarEdge SE7600A",
  "serialNumber": "SE7600A-12345",
  "capacity": 7.6, // kW
  "installationDate": "2023-06-15T00:00:00Z",
  "status": "online", // "online", "offline", "warning", "fault"
  "lastCommunication": "2024-01-01T12:00:00Z",
  "firmware": "1.2.3",
  "configuration": {
    "panelCount": 10,
    "nominalVoltage": 240,
    "maxCurrent": 25
  },
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

## TimeScale DB Tables (Time-Series Data)

### Device Metrics Table
```sql
CREATE TABLE device_metrics (
  time TIMESTAMPTZ NOT NULL,
  device_id TEXT NOT NULL,
  metric_type TEXT NOT NULL, -- 'voltage', 'current', 'power', 'temperature'
  metric_name TEXT NOT NULL, -- 'PV1', 'PV2', 'input1', 'output1', etc.
  value DOUBLE PRECISION NOT NULL,
  unit TEXT NOT NULL, -- 'V', 'A', 'W', 'C'
  quality INTEGER DEFAULT 100, -- Data quality 0-100
  PRIMARY KEY (time, device_id, metric_type, metric_name)
);

-- Create hypertable for time-series optimization
SELECT create_hypertable('device_metrics', 'time');

-- Create indexes for efficient querying
CREATE INDEX idx_device_metrics_device_time ON device_metrics (device_id, time DESC);
CREATE INDEX idx_device_metrics_type_time ON device_metrics (metric_type, time DESC);
```

### Device Events Table
```sql
CREATE TABLE device_events (
  time TIMESTAMPTZ NOT NULL,
  device_id TEXT NOT NULL,
  event_type TEXT NOT NULL, -- 'alarm', 'warning', 'info'
  event_code TEXT NOT NULL,
  message TEXT,
  severity INTEGER NOT NULL, -- 1-5 (1=info, 5=critical)
  acknowledged BOOLEAN DEFAULT FALSE,
  acknowledged_by TEXT,
  acknowledged_at TIMESTAMPTZ,
  PRIMARY KEY (time, device_id, event_type)
);

SELECT create_hypertable('device_events', 'time');
CREATE INDEX idx_device_events_device_time ON device_events (device_id, time DESC);
```

## API Endpoints Required

### Authentication Endpoints
- POST /api/auth/login
- POST /api/auth/register  
- POST /api/auth/logout
- GET /api/auth/me

### Plants Endpoints
- GET /api/plants
- GET /api/plants/:plantId
- GET /api/plants/:plantId/devices

### Devices Endpoints
- GET /api/devices
- GET /api/devices/:deviceId
- GET /api/devices/:deviceId/timeseries
- POST /api/devices/:deviceId/timeseries/batch

### Time-Series Data Endpoints
- GET /api/devices/:deviceId/timeseries?metric=:metric&timeRange=:range&startTime=:start&endTime=:end
- GET /api/devices/:deviceId/metrics/latest
- GET /api/devices/:deviceId/events

## Sample API Response Formats

### Time-Series Data Response
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

### Device Status Response
```json
{
  "deviceId": "device-123",
  "status": "online",
  "lastUpdate": "2024-01-01T12:00:00Z",
  "currentMetrics": {
    "totalPower": 4520.5,
    "efficiency": 94.2,
    "temperature": 42.1,
    "uptime": 99.8
  },
  "alerts": [
    {
      "type": "warning",
      "message": "Panel PV3 voltage slightly below normal",
      "timestamp": "2024-01-01T11:45:00Z"
    }
  ]
}
```

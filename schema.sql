-- Simplified SQL schema for solar dashboard project
-- Supports user registration with required and optional fields
-- Drops all tables and types to ensure clean state
-- Run in a test database; remove DROP statements in production

-- Drop existing tables and types
DROP TABLE IF EXISTS error_logs CASCADE;
DROP TABLE IF EXISTS customer_metrics CASCADE;
DROP TABLE IF EXISTS device_data_historical CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS fault_logs CASCADE;
DROP TABLE IF EXISTS weather_data CASCADE;
DROP TABLE IF EXISTS devices CASCADE;
DROP TABLE IF EXISTS plants CASCADE;
DROP TABLE IF EXISTS api_credentials CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TYPE IF EXISTS api_provider_type CASCADE;
DROP TYPE IF EXISTS severity_type CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;

-- Create ENUM types
CREATE TYPE api_provider_type AS ENUM ('shinemonitor', 'solarman', 'soliscloud');
CREATE TYPE severity_type AS ENUM ('low', 'medium', 'high');

-- Create users table
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    usertype TEXT NOT NULL CHECK (usertype IN ('customer', 'installer')),
    profile JSONB NOT NULL DEFAULT '{}', -- Stores address, panelBrand, panelCapacity, panelType, inverterBrand, inverterCapacity, whatsappNumber
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

INSERT INTO users (id, username, name, email, password_hash, usertype, profile)
VALUES 
    ('507f1f77bcf86cd799439011', 'demo', 'Demo User', 'demo@example.com', '$2b$12$mcZLDV4fPyhoKsGIUyk03eQxkANE0ifIFYJpITZAAb1s61BE.Z9Oe', 'customer', '{"installationId": "INST-12345", "address": "123 Solar Street, CA", "whatsappNumber": "+1234567890"}'),
    ('507f1f77bcf86cd799439012', 'admin', 'Admin User', 'admin@example.com', '$2b$12$b4Dp/13Bh2bN/5nlpKxBrer3sN0zRxrnSPlEk7Ex8lKlNGog6eedu', 'installer', '{"companyName": "Solar Install Co", "licenseNumber": "LIC-789", "phoneNumber": "+1-555-0123", "panelBrand": "SunPower", "panelCapacity": "5.0", "panelType": "monocrystalline", "inverterBrand": "SMA", "inverterCapacity": "4.0", "whatsappNumber": "+1987654321"}');

-- Create customers table
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    customer_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create api_credentials table
CREATE TABLE api_credentials (
    credential_id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    customer_id TEXT NOT NULL,
    api_provider api_provider_type NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    api_key TEXT,
    api_secret TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Create plants table
CREATE TABLE plants (
    plant_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    plant_name TEXT NOT NULL,
    capacity DOUBLE PRECISION CHECK (capacity >= 0),
    total_energy DOUBLE PRECISION CHECK (total_energy >= 0),
    install_date DATE,
    location TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Create devices table
CREATE TABLE devices (
    device_sn TEXT PRIMARY KEY,
    plant_id TEXT NOT NULL,
    inverter_model TEXT,
    panel_model TEXT,
    pv_count INTEGER CHECK (pv_count >= 0),
    string_count INTEGER CHECK (string_count >= 0),
    first_install_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE
);

-- Create weather_data table
CREATE TABLE weather_data (
    plant_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature DOUBLE PRECISION,
    irradiance DOUBLE PRECISION CHECK (irradiance >= 0),
    humidity DOUBLE PRECISION CHECK (humidity >= 0 AND humidity <= 100),
    wind_speed DOUBLE PRECISION CHECK (wind_speed >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE,
    PRIMARY KEY (plant_id, timestamp)
);
SELECT create_hypertable('weather_data', 'timestamp');

-- Create device_data_historical table
CREATE TABLE device_data_historical (
    device_sn TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    pv01_voltage DOUBLE PRECISION CHECK (pv01_voltage >= 0 AND pv01_voltage <= 1000),
    pv01_current DOUBLE PRECISION CHECK (pv01_current >= 0 AND pv01_current <= 50),
    pv02_voltage DOUBLE PRECISION CHECK (pv02_voltage >= 0 AND pv02_voltage <= 1000),
    pv02_current DOUBLE PRECISION CHECK (pv02_current >= 0 AND pv02_current <= 50),
    pv03_voltage DOUBLE PRECISION CHECK (pv03_voltage >= 0 AND pv03_voltage <= 1000),
    pv03_current DOUBLE PRECISION CHECK (pv03_current >= 0 AND pv03_current <= 50),
    pv04_voltage DOUBLE PRECISION CHECK (pv04_voltage >= 0 AND pv04_voltage <= 1000),
    pv04_current DOUBLE PRECISION CHECK (pv04_current >= 0 AND pv04_current <= 50),
    pv05_voltage DOUBLE PRECISION CHECK (pv05_voltage >= 0 AND pv05_voltage <= 1000),
    pv05_current DOUBLE PRECISION CHECK (pv05_current >= 0 AND pv05_current <= 50),
    pv06_voltage DOUBLE PRECISION CHECK (pv06_voltage >= 0 AND pv06_voltage <= 1000),
    pv06_current DOUBLE PRECISION CHECK (pv06_current >= 0 AND pv06_current <= 50),
    pv07_voltage DOUBLE PRECISION CHECK (pv07_voltage >= 0 AND pv07_voltage <= 1000),
    pv07_current DOUBLE PRECISION CHECK (pv07_current >= 0 AND pv07_current <= 50),
    pv08_voltage DOUBLE PRECISION CHECK (pv08_voltage >= 0 AND pv08_voltage <= 1000),
    pv08_current DOUBLE PRECISION CHECK (pv08_current >= 0 AND pv08_current <= 50),
    pv09_voltage DOUBLE PRECISION CHECK (pv09_voltage >= 0 AND pv09_voltage <= 1000),
    pv09_current DOUBLE PRECISION CHECK (pv09_current >= 0 AND pv09_current <= 50),
    pv10_voltage DOUBLE PRECISION CHECK (pv10_voltage >= 0 AND pv10_voltage <= 1000),
    pv10_current DOUBLE PRECISION CHECK (pv10_current >= 0 AND pv10_current <= 50),
    pv11_voltage DOUBLE PRECISION CHECK (pv11_voltage >= 0 AND pv11_voltage <= 1000),
    pv11_current DOUBLE PRECISION CHECK (pv11_current >= 0 AND pv11_current <= 50),
    pv12_voltage DOUBLE PRECISION CHECK (pv12_voltage >= 0 AND pv12_voltage <= 1000),
    pv12_current DOUBLE PRECISION CHECK (pv12_current >= 0 AND pv12_current <= 50),
    r_voltage DOUBLE PRECISION CHECK (r_voltage >= 0 AND r_voltage <= 325),
    s_voltage DOUBLE PRECISION CHECK (s_voltage >= 0 AND s_voltage <= 325),
    t_voltage DOUBLE PRECISION CHECK (t_voltage >= 0 AND t_voltage <= 325),
    r_current DOUBLE PRECISION CHECK (r_current >= 0 AND r_current <= 500),
    s_current DOUBLE PRECISION CHECK (s_current >= 0 AND s_current <= 500),
    t_current DOUBLE PRECISION CHECK (t_current >= 0 AND t_current <= 500),
    rs_voltage DOUBLE PRECISION CHECK (rs_voltage >= 0 AND rs_voltage <= 500),
    st_voltage DOUBLE PRECISION CHECK (st_voltage >= 0 AND st_voltage <= 500),
    tr_voltage DOUBLE PRECISION CHECK (tr_voltage >= 0 AND tr_voltage <= 500),
    frequency DOUBLE PRECISION CHECK (frequency >= 0 AND frequency <= 70),
    total_power DOUBLE PRECISION CHECK (total_power >= 0),
    reactive_power DOUBLE PRECISION CHECK (reactive_power >= -100000 AND reactive_power <= 100000),
    energy_today DOUBLE PRECISION CHECK (energy_today >= 0 AND energy_today <= 20000),
    cuf DOUBLE PRECISION CHECK (cuf >= 0 AND cuf <= 100),
    pr DOUBLE PRECISION CHECK (pr >= 0 AND pr <= 100),
    state TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (device_sn) REFERENCES devices(device_sn) ON DELETE CASCADE,
    PRIMARY KEY (device_sn, timestamp)
);
SELECT create_hypertable('device_data_historical', 'timestamp');

-- Create predictions table
CREATE TABLE predictions (
    prediction_id SERIAL NOT NULL,
    device_sn TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    predicted_energy DOUBLE PRECISION CHECK (predicted_energy >= 0),
    predicted_pr DOUBLE PRECISION CHECK (predicted_pr >= 0 AND predicted_pr <= 100),
    confidence_score DOUBLE PRECISION CHECK (confidence_score >= 0 AND confidence_score <= 1),
    model_version TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (device_sn) REFERENCES devices(device_sn) ON DELETE CASCADE,
    PRIMARY KEY (prediction_id, timestamp)
);
SELECT create_hypertable('predictions', 'timestamp');

-- Create fault_logs table
CREATE TABLE fault_logs (
    fault_id SERIAL NOT NULL,
    device_sn TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    fault_code TEXT,
    fault_description TEXT,
    severity severity_type,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (device_sn) REFERENCES devices(device_sn) ON DELETE CASCADE,
    PRIMARY KEY (fault_id, timestamp)
);
SELECT create_hypertable('fault_logs', 'timestamp');

-- Create error_logs table
CREATE TABLE error_logs (
    error_id SERIAL NOT NULL,
    customer_id TEXT,
    device_sn TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    api_provider api_provider_type,
    field_name TEXT,
    field_value TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (error_id, timestamp)
);
SELECT create_hypertable('error_logs', 'timestamp');

-- Create materialized view for admin panel metrics
CREATE MATERIALIZED VIEW customer_metrics AS
SELECT customer_id, 0.0 AS total_energy_today, 0.0 AS avg_pr, 0 AS active_devices
FROM customers
WITH NO DATA;

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers for updated_at
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customers_updated_at
BEFORE UPDATE ON customers
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_credentials_updated_at
BEFORE UPDATE ON api_credentials
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plants_updated_at
BEFORE UPDATE ON plants
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at
BEFORE UPDATE ON devices
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_weather_data_updated_at
BEFORE UPDATE ON weather_data
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_device_data_historical_updated_at
BEFORE UPDATE ON device_data_historical
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_predictions_updated_at
BEFORE UPDATE ON predictions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fault_logs_updated_at
BEFORE UPDATE ON fault_logs
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_error_logs_updated_at
BEFORE UPDATE ON error_logs
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
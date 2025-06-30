-- Corrected final SQL schema for solar dashboard project
-- Supports dynamic table generation for per-customer device_data tables
-- Uses TEXT instead of VARCHAR to follow PostgreSQL best practices
-- Includes shared device_data_historical, fault_logs, predictions, error_logs
-- Adds materialized view for admin metrics and trigger for new customer tables
-- Designed for ~800-1,000 customers, ~10 devices each, with TimescaleDB
-- Run in a test database; remove DROP statements in production

-- Drop existing tables if they exist (for testing; remove in production)
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

-- Create ENUM type for api_provider
CREATE TYPE api_provider_type AS ENUM ('shinemonitor', 'solarman', 'soliscloud');

-- Create ENUM type for fault severity
CREATE TYPE severity_type AS ENUM ('low', 'medium', 'high');

-- Create customers table (central hub)
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
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

-- Create device_data_historical table (shared for all customers)
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

-- Create materialized view for admin panel metrics (initially empty)
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

-- Create trigger function to generate per-customer device_data table
CREATE OR REPLACE FUNCTION create_customer_device_table()
RETURNS TRIGGER AS $$
DECLARE
    safe_customer_id TEXT;
    table_exists BOOLEAN;
BEGIN
    -- Validate customer_id
    IF NEW.customer_id IS NULL OR NEW.customer_id = '' THEN
        INSERT INTO error_logs (
            customer_id, device_sn, timestamp, api_provider, field_name, field_value, error_message, created_at
        ) VALUES (
            NULL, NULL, NOW(), NULL, 'customer_id', NEW.customer_id, 'Invalid customer_id: cannot be null or empty', NOW()
        );
        RAISE EXCEPTION 'Invalid customer_id: cannot be null or empty';
    END IF;

    -- Sanitize customer_id
    safe_customer_id := REGEXP_REPLACE(LOWER(NEW.customer_id), '[^a-z0-9_]', '_');
    safe_customer_id := LEFT(safe_customer_id, 63);

    -- Ensure safe_customer_id is not empty
    IF safe_customer_id = '' THEN
        INSERT INTO error_logs (
            customer_id, device_sn, timestamp, api_provider, field_name, field_value, error_message, created_at
        ) VALUES (
            NEW.customer_id, NULL, NOW(), NULL, 'customer_id', NEW.customer_id, 'Invalid customer_id after sanitization', NOW()
        );
        RAISE EXCEPTION 'Invalid customer_id after sanitization: %', NEW.customer_id;
    END IF;

    -- Check if table exists
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = format('customer_%I_device_data', safe_customer_id)
    ) INTO table_exists;

    IF NOT table_exists THEN
        -- Create customer_{safe_customer_id}_device_data table
        EXECUTE format('
            CREATE TABLE customer_%I_device_data (
                device_sn TEXT NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                pv01_voltage DOUBLE PRECISION CHECK (pv01_voltage IS NULL OR (pv01_voltage >= 0 AND pv01_voltage <= 1000)),
                pv01_current DOUBLE PRECISION CHECK (pv01_current IS NULL OR (pv01_current >= 0 AND pv01_current <= 50)),
                pv02_voltage DOUBLE PRECISION CHECK (pv02_voltage IS NULL OR (pv02_voltage >= 0 AND pv02_voltage <= 1000)),
                pv02_current DOUBLE PRECISION CHECK (pv02_current IS NULL OR (pv02_current >= 0 AND pv02_current <= 50)),
                pv03_voltage DOUBLE PRECISION CHECK (pv03_voltage IS NULL OR (pv03_voltage >= 0 AND pv03_voltage <= 1000)),
                pv03_current DOUBLE PRECISION CHECK (pv03_current IS NULL OR (pv03_current >= 0 AND pv03_current <= 50)),
                pv04_voltage DOUBLE PRECISION CHECK (pv04_voltage IS NULL OR (pv04_voltage >= 0 AND pv04_voltage <= 1000)),
                pv04_current DOUBLE PRECISION CHECK (pv04_current IS NULL OR (pv04_current >= 0 AND pv04_current <= 50)),
                pv05_voltage DOUBLE PRECISION CHECK (pv05_voltage IS NULL OR (pv05_voltage >= 0 AND pv05_voltage <= 1000)),
                pv05_current DOUBLE PRECISION CHECK (pv05_current IS NULL OR (pv05_current >= 0 AND pv05_current <= 50)),
                pv06_voltage DOUBLE PRECISION CHECK (pv06_voltage IS NULL OR (pv06_voltage >= 0 AND pv06_voltage <= 1000)),
                pv06_current DOUBLE PRECISION CHECK (pv06_current IS NULL OR (pv06_current >= 0 AND pv06_current <= 50)),
                pv07_voltage DOUBLE PRECISION CHECK (pv07_voltage IS NULL OR (pv07_voltage >= 0 AND pv07_voltage <= 1000)),
                pv07_current DOUBLE PRECISION CHECK (pv07_current IS NULL OR (pv07_current >= 0 AND pv07_current <= 50)),
                pv08_voltage DOUBLE PRECISION CHECK (pv08_voltage IS NULL OR (pv08_voltage >= 0 AND pv08_voltage <= 1000)),
                pv08_current DOUBLE PRECISION CHECK (pv08_current IS NULL OR (pv08_current >= 0 AND pv08_current <= 50)),
                pv09_voltage DOUBLE PRECISION CHECK (pv09_voltage IS NULL OR (pv09_voltage >= 0 AND pv09_voltage <= 1000)),
                pv09_current DOUBLE PRECISION CHECK (pv09_current IS NULL OR (pv09_current >= 0 AND pv09_current <= 50)),
                pv10_voltage DOUBLE PRECISION CHECK (pv10_voltage IS NULL OR (pv10_voltage >= 0 AND pv10_voltage <= 1000)),
                pv10_current DOUBLE PRECISION CHECK (pv10_current IS NULL OR (pv10_current >= 0 AND pv10_current <= 50)),
                pv11_voltage DOUBLE PRECISION CHECK (pv11_voltage IS NULL OR (pv11_voltage >= 0 AND pv11_voltage <= 1000)),
                pv11_current DOUBLE PRECISION CHECK (pv11_current IS NULL OR (pv11_current >= 0 AND pv11_current <= 50)),
                pv12_voltage DOUBLE PRECISION CHECK (pv12_voltage IS NULL OR (pv12_voltage >= 0 AND pv12_voltage <= 1000)),
                pv12_current DOUBLE PRECISION CHECK (pv12_current IS NULL OR (pv12_current >= 0 AND pv12_current <= 50)),
                r_voltage DOUBLE PRECISION CHECK (r_voltage IS NULL OR (r_voltage >= 0 AND r_voltage <= 300)),
                s_voltage DOUBLE PRECISION CHECK (s_voltage IS NULL OR (s_voltage >= 0 AND s_voltage <= 300)),
                t_voltage DOUBLE PRECISION CHECK (t_voltage IS NULL OR (t_voltage >= 0 AND t_voltage <= 300)),
                r_current DOUBLE PRECISION CHECK (r_current IS NULL OR (r_current >= 0 AND r_current <= 100)),
                s_current DOUBLE PRECISION CHECK (s_current IS NULL OR (s_current >= 0 AND s_current <= 100)),
                t_current DOUBLE PRECISION CHECK (t_current IS NULL OR (t_current >= 0 AND t_current <= 100)),
                rs_voltage DOUBLE PRECISION CHECK (rs_voltage IS NULL OR (rs_voltage >= 0 AND rs_voltage <= 500)),
                st_voltage DOUBLE PRECISION CHECK (st_voltage IS NULL OR (st_voltage >= 0 AND st_voltage <= 500)),
                tr_voltage DOUBLE PRECISION CHECK (tr_voltage IS NULL OR (tr_voltage >= 0 AND tr_voltage <= 500)),
                frequency DOUBLE PRECISION CHECK (frequency IS NULL OR (frequency >= 0 AND frequency <= 70)),
                total_power DOUBLE PRECISION CHECK (total_power IS NULL OR (total_power >= 0 AND total_power <= 100000)),
                reactive_power DOUBLE PRECISION CHECK (reactive_power IS NULL OR (reactive_power >= -100000 AND reactive_power <= 100000)),
                energy_today DOUBLE PRECISION CHECK (energy_today IS NULL OR (energy_today >= 0 AND energy_today <= 1000)),
                cuf DOUBLE PRECISION CHECK (cuf IS NULL OR (cuf >= 0 AND cuf <= 100)),
                pr DOUBLE PRECISION CHECK (pr IS NULL OR (pr >= 0 AND pr <= 100)),
                state TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ,
                FOREIGN KEY (device_sn) REFERENCES devices(device_sn) ON DELETE CASCADE,
                PRIMARY KEY (device_sn, timestamp)
            );
            SELECT create_hypertable(''customer_%I_device_data'', ''timestamp'');
            CREATE TRIGGER update_customer_%I_device_data_updated_at
            BEFORE UPDATE ON customer_%I_device_data
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        ', safe_customer_id, safe_customer_id, safe_customer_id, safe_customer_id);
    END IF;
    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        INSERT INTO error_logs (
            customer_id, device_sn, timestamp, api_provider, field_name, field_value, error_message, created_at
        ) VALUES (
            NEW.customer_id, NULL, NOW(), NULL, 'trigger_create_customer_device_table', NEW.customer_id, SQLERRM, NOW()
        );
        RAISE EXCEPTION 'Failed to create customer table: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers for updated_at
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

-- Create trigger for per-customer table creation
CREATE TRIGGER trigger_create_customer_device_table
AFTER INSERT ON customers
FOR EACH ROW EXECUTE FUNCTION create_customer_device_table();

-- Schedule move_old_data_to_historical (weekly; assumes function exists)
SELECT add_job('move_old_data_to_historical', '1 week', initial_start => '2025-06-17 00:00:00+05:30');
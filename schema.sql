-- Drop existing tables if they exist (for testing; remove in production)
DROP TABLE IF EXISTS device_data_current CASCADE;
DROP TABLE IF EXISTS device_data_historical CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS fault_logs CASCADE;
DROP TABLE IF EXISTS weather_data CASCADE;
DROP TABLE IF EXISTS devices CASCADE;
DROP TABLE IF EXISTS plants CASCADE;
DROP TABLE IF EXISTS api_credentials CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- Create an ENUM type for api_provider
CREATE TYPE api_provider_type AS ENUM ('shinemonitor', 'solarman', 'soliscloud');

-- Create an ENUM type for fault severity
CREATE TYPE severity_type AS ENUM ('low', 'medium', 'high');

-- Create the customers table (central hub)
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create the api_credentials table
CREATE TABLE api_credentials (
    credential_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    customer_id VARCHAR(50) NOT NULL,
    api_provider api_provider_type NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    api_key VARCHAR(255),
    api_secret VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Create the plants table
CREATE TABLE plants (
    plant_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    plant_name VARCHAR(100) NOT NULL,
    capacity DOUBLE PRECISION CHECK (capacity >= 0), -- in kW
    total_energy DOUBLE PRECISION CHECK (total_energy >= 0), -- in kWh
    install_date DATE,
    location TEXT, -- Could be expanded to latitude/longitude
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Create the devices table
CREATE TABLE devices (
    device_sn VARCHAR(50) PRIMARY KEY,
    plant_id VARCHAR(50) NOT NULL,
    inverter_model VARCHAR(100),
    panel_model VARCHAR(100),
    pv_count INTEGER CHECK (pv_count >= 0), -- Number of PV panels
    string_count INTEGER CHECK (string_count >= 0), -- Number of strings
    first_install_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE
);

-- Create the weather_data table (linked to plants)
CREATE TABLE weather_data (
    plant_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature DOUBLE PRECISION, -- in Celsius
    irradiance DOUBLE PRECISION CHECK (irradiance >= 0), -- in W/m²
    humidity DOUBLE PRECISION CHECK (humidity >= 0 AND humidity <= 100), -- in %
    wind_speed DOUBLE PRECISION CHECK (wind_speed >= 0), -- in m/s
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE
);

-- Convert weather_data to a TimescaleDB hypertable
SELECT create_hypertable('weather_data', 'timestamp');

-- Add the primary key after creating the hypertable
ALTER TABLE weather_data ADD PRIMARY KEY (plant_id, timestamp);

-- Create the device_data_current table (current day/week data) without primary key initially
CREATE TABLE device_data_current (
    device_sn VARCHAR(50) NOT NULL,
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
    r_voltage DOUBLE PRECISION CHECK (r_voltage >= 0 AND r_voltage <= 300),
    s_voltage DOUBLE PRECISION CHECK (s_voltage >= 0 AND s_voltage <= 300),
    t_voltage DOUBLE PRECISION CHECK (t_voltage >= 0 AND t_voltage <= 300),
    r_current DOUBLE PRECISION CHECK (r_current >= 0 AND r_current <= 100),
    s_current DOUBLE PRECISION CHECK (s_current >= 0 AND s_current <= 100),
    t_current DOUBLE PRECISION CHECK (t_current >= 0 AND t_current <= 100),
    rs_voltage DOUBLE PRECISION CHECK (rs_voltage >= 0 AND rs_voltage <= 500),
    st_voltage DOUBLE PRECISION CHECK (st_voltage >= 0 AND st_voltage <= 500),
    tr_voltage DOUBLE PRECISION CHECK (tr_voltage >= 0 AND tr_voltage <= 500),
    frequency DOUBLE PRECISION CHECK (frequency >= 0 AND frequency <= 70),
    total_power DOUBLE PRECISION CHECK (total_power >= 0 AND total_power <= 100000),
    reactive_power DOUBLE PRECISION CHECK (reactive_power >= -100000 AND reactive_power <= 100000),
    energy_today DOUBLE PRECISION CHECK (energy_today >= 0 AND energy_today <= 1000),
    cuf DOUBLE PRECISION CHECK (cuf >= 0 AND cuf <= 100), -- Capacity Utilization Factor
    pr DOUBLE PRECISION CHECK (pr >= 0 AND pr <= 100), -- Performance Ratio
    state TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (device_sn) REFERENCES devices(device_sn) ON DELETE CASCADE
);

-- Convert device_data_current to a TimescaleDB hypertable
SELECT create_hypertable('device_data_current', 'timestamp');

-- Add the primary key after creating the hypertable
ALTER TABLE device_data_current ADD PRIMARY KEY (device_sn, timestamp);

-- Create the device_data_historical table (historical data) without primary key initially
CREATE TABLE device_data_historical (
    device_sn VARCHAR(50) NOT NULL,
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
    r_voltage DOUBLE PRECISION CHECK (r_voltage >= 0 AND r_voltage <= 300),
    s_voltage DOUBLE PRECISION CHECK (s_voltage >= 0 AND s_voltage <= 300),
    t_voltage DOUBLE PRECISION CHECK (t_voltage >= 0 AND t_voltage <= 300),
    r_current DOUBLE PRECISION CHECK (r_current >= 0 AND r_current <= 100),
    s_current DOUBLE PRECISION CHECK (s_current >= 0 AND s_current <= 100),
    t_current DOUBLE PRECISION CHECK (t_current >= 0 AND t_current <= 100),
    rs_voltage DOUBLE PRECISION CHECK (rs_voltage >= 0 AND rs_voltage <= 500),
    st_voltage DOUBLE PRECISION CHECK (st_voltage >= 0 AND st_voltage <= 500),
    tr_voltage DOUBLE PRECISION CHECK (tr_voltage >= 0 AND tr_voltage <= 500),
    frequency DOUBLE PRECISION CHECK (frequency >= 0 AND frequency <= 70),
    total_power DOUBLE PRECISION CHECK (total_power >= 0 AND total_power <= 100000),
    reactive_power DOUBLE PRECISION CHECK (reactive_power >= -100000 AND reactive_power <= 100000),
    energy_today DOUBLE PRECISION CHECK (energy_today >= 0 AND energy_today <= 1000),
    cuf DOUBLE PRECISION CHECK (cuf >= 0 AND cuf <= 100), -- Capacity Utilization Factor
    pr DOUBLE PRECISION CHECK (pr >= 0 AND pr <= 100), -- Performance Ratio
    state TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (device_sn) REFERENCES devices(device_sn) ON DELETE CASCADE
);

-- Convert device_data_historical to a TimescaleDB hypertable
SELECT create_hypertable('device_data_historical', 'timestamp');

-- Add the primary key after creating the hypertable
ALTER TABLE device_data_historical ADD PRIMARY KEY (device_sn, timestamp);

-- Create the predictions table (for predictive analytics) without primary key
CREATE TABLE predictions (
    prediction_id SERIAL NOT NULL,
    device_sn VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    predicted_energy DOUBLE PRECISION CHECK (predicted_energy >= 0), -- Predicted energy output (kWh)
    predicted_pr DOUBLE PRECISION CHECK (predicted_pr >= 0 AND predicted_pr <= 100), -- Predicted Performance Ratio
    confidence_score DOUBLE PRECISION CHECK (confidence_score >= 0 AND confidence_score <= 1), -- Confidence in the prediction (0 to 1)
    model_version VARCHAR(50), -- Version of the prediction model
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (device_sn) REFERENCES devices(device_sn) ON DELETE CASCADE
);

-- Convert predictions to a TimescaleDB hypertable
SELECT create_hypertable('predictions', 'timestamp');

-- Add a composite primary key
ALTER TABLE predictions ADD PRIMARY KEY (prediction_id, timestamp);

-- Create the fault_logs table (for diagnostics) without primary key
CREATE TABLE fault_logs (
    fault_id SERIAL NOT NULL,
    device_sn VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    fault_code VARCHAR(50),
    fault_description TEXT,
    severity severity_type, -- e.g., 'low', 'medium', 'high'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (device_sn) REFERENCES devices(device_sn) ON DELETE CASCADE
);

-- Convert fault_logs to a TimescaleDB hypertable
SELECT create_hypertable('fault_logs', 'timestamp');

-- Add a composite primary key
ALTER TABLE fault_logs ADD PRIMARY KEY (fault_id, timestamp);

-- Create a procedure to move data from device_data_current to device_data_historical
CREATE OR REPLACE PROCEDURE move_old_data_to_historical(job_id int, config jsonb)
LANGUAGE PLPGSQL
AS $$
BEGIN
    -- Copy data older than 7 days to device_data_historical
    INSERT INTO device_data_historical
    SELECT * FROM device_data_current
    WHERE timestamp < NOW() - INTERVAL '7 days'
    ON CONFLICT (device_sn, timestamp) DO NOTHING;

    -- Delete the copied data from device_data_current
    DELETE FROM device_data_current
    WHERE timestamp < NOW() - INTERVAL '7 days';

    -- Log the operation
    RAISE NOTICE 'Moved old data from device_data_current to device_data_historical for job %', job_id;
END;
$$;

-- Schedule the procedure to run weekly (adjust the start time if needed)
SELECT add_job('move_old_data_to_historical', '1 week', initial_start => '2025-06-17 00:00:00+05:30');

-- Trigger function for updated_at (shared across tables)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at on all tables
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_credentials_updated_at
    BEFORE UPDATE ON api_credentials
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plants_updated_at
    BEFORE UPDATE ON plants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_weather_data_updated_at
    BEFORE UPDATE ON weather_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_device_data_current_updated_at
    BEFORE UPDATE ON device_data_current
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_device_data_historical_updated_at
    BEFORE UPDATE ON device_data_historical
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_predictions_updated_at
    BEFORE UPDATE ON predictions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fault_logs_updated_at
    BEFORE UPDATE ON fault_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
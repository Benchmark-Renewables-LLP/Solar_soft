-- Drop existing tables if they exist (for testing; remove in production)
DROP TABLE IF EXISTS device_data_current CASCADE;
DROP TABLE IF EXISTS device_data_historical CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS fault_logs CASCADE;
DROP TABLE IF EXISTS devices CASCADE;
DROP TABLE IF EXISTS plants CASCADE;
DROP TABLE IF EXISTS api_credentials CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- Create the customers table (central hub)
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create the api_credentials table
CREATE TABLE api_credentials (
    credential_id SERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL,
    api_provider TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    api_key TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Create the plants table
CREATE TABLE plants (
    plant_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    plant_name TEXT NOT NULL,
    capacity DOUBLE PRECISION, -- in kW
    total_energy DOUBLE PRECISION, -- in kWh
    install_date DATE,
    location TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Create the devices table
CREATE TABLE devices (
    device_sn TEXT PRIMARY KEY,
    plant_id TEXT NOT NULL,
    inverter_model TEXT,
    panel_model TEXT,
    pv_count INTEGER, -- Number of PV panels
    string_count INTEGER, -- Number of strings
    first_install_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE
);

-- Create the device_data_current table (current day/week data) without primary key initially
CREATE TABLE device_data_current (
    device_sn TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    pv01_voltage DOUBLE PRECISION,
    pv01_current DOUBLE PRECISION,
    pv02_voltage DOUBLE PRECISION,
    pv02_current DOUBLE PRECISION,
    pv03_voltage DOUBLE PRECISION,
    pv03_current DOUBLE PRECISION,
    pv04_voltage DOUBLE PRECISION,
    pv04_current DOUBLE PRECISION,
    pv05_voltage DOUBLE PRECISION,
    pv05_current DOUBLE PRECISION,
    pv06_voltage DOUBLE PRECISION,
    pv06_current DOUBLE PRECISION,
    pv07_voltage DOUBLE PRECISION,
    pv07_current DOUBLE PRECISION,
    pv08_voltage DOUBLE PRECISION,
    pv08_current DOUBLE PRECISION,
    pv09_voltage DOUBLE PRECISION,
    pv09_current DOUBLE PRECISION,
    pv10_voltage DOUBLE PRECISION,
    pv10_current DOUBLE PRECISION,
    pv11_voltage DOUBLE PRECISION,
    pv11_current DOUBLE PRECISION,
    pv12_voltage DOUBLE PRECISION,
    pv12_current DOUBLE PRECISION,
    r_voltage DOUBLE PRECISION,
    s_voltage DOUBLE PRECISION,
    t_voltage DOUBLE PRECISION,
    r_current DOUBLE PRECISION,
    s_current DOUBLE PRECISION,
    t_current DOUBLE PRECISION,
    rs_voltage DOUBLE PRECISION,
    st_voltage DOUBLE PRECISION,
    tr_voltage DOUBLE PRECISION,
    frequency DOUBLE PRECISION,
    total_power DOUBLE PRECISION,
    reactive_power DOUBLE PRECISION,
    energy_today DOUBLE PRECISION,
    cuf DOUBLE PRECISION, -- Capacity Utilization Factor
    pr DOUBLE PRECISION, -- Performance Ratio
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
    device_sn TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    pv01_voltage DOUBLE PRECISION,
    pv01_current DOUBLE PRECISION,
    pv02_voltage DOUBLE PRECISION,
    pv02_current DOUBLE PRECISION,
    pv03_voltage DOUBLE PRECISION,
    pv03_current DOUBLE PRECISION,
    pv04_voltage DOUBLE PRECISION,
    pv04_current DOUBLE PRECISION,
    pv05_voltage DOUBLE PRECISION,
    pv05_current DOUBLE PRECISION,
    pv06_voltage DOUBLE PRECISION,
    pv06_current DOUBLE PRECISION,
    pv07_voltage DOUBLE PRECISION,
    pv07_current DOUBLE PRECISION,
    pv08_voltage DOUBLE PRECISION,
    pv08_current DOUBLE PRECISION,
    pv09_voltage DOUBLE PRECISION,
    pv09_current DOUBLE PRECISION,
    pv10_voltage DOUBLE PRECISION,
    pv10_current DOUBLE PRECISION,
    pv11_voltage DOUBLE PRECISION,
    pv11_current DOUBLE PRECISION,
    pv12_voltage DOUBLE PRECISION,
    pv12_current DOUBLE PRECISION,
    r_voltage DOUBLE PRECISION,
    s_voltage DOUBLE PRECISION,
    t_voltage DOUBLE PRECISION,
    r_current DOUBLE PRECISION,
    s_current DOUBLE PRECISION,
    t_current DOUBLE PRECISION,
    rs_voltage DOUBLE PRECISION,
    st_voltage DOUBLE PRECISION,
    tr_voltage DOUBLE PRECISION,
    frequency DOUBLE PRECISION,
    total_power DOUBLE PRECISION,
    reactive_power DOUBLE PRECISION,
    energy_today DOUBLE PRECISION,
    cuf DOUBLE PRECISION, -- Capacity Utilization Factor
    pr DOUBLE PRECISION, -- Performance Ratio
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
    device_sn TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    predicted_energy DOUBLE PRECISION, -- Predicted energy output (kWh)
    predicted_pr DOUBLE PRECISION, -- Predicted Performance Ratio
    confidence_score DOUBLE PRECISION, -- Confidence in the prediction (0 to 1)
    model_version TEXT, -- Version of the prediction model
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (device_sn) REFERENCES devices(device_sn) ON DELETE CASCADE
);

-- Convert predictions to a TimescaleDB hypertable
SELECT create_hypertable('predictions', 'timestamp');

-- Create the fault_logs table (for diagnostics) without primary key
CREATE TABLE fault_logs (
    fault_id SERIAL NOT NULL,
    device_sn TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    fault_code TEXT,
    fault_description TEXT,
    severity TEXT, -- e.g., 'low', 'medium', 'high'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (device_sn) REFERENCES devices(device_sn) ON DELETE CASCADE
);

-- Convert fault_logs to a TimescaleDB hypertable
SELECT create_hypertable('fault_logs', 'timestamp');

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

-- Schedule the procedure to run weekly
SELECT add_job('move_old_data_to_historical', '1 week', initial_start => '2025-06-10 00:00:00+05:30');

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
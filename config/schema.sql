-- Schema for fetch_historic_data.py with auto-generated customer_id, triggers, and CHECK constraints
-- Defines tables for customers, API credentials, plants, devices, and historical device data
-- Generated based on script analysis on June 20, 2025

-- Function to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
COMMENT ON FUNCTION update_updated_at_column IS 'Updates updated_at column to current timestamp on row update';

-- Customers table with auto-generated ID
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    external_customer_id TEXT UNIQUE NOT NULL,
    customer_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
COMMENT ON TABLE customers IS 'Stores customer information with auto-generated ID and external identifier from credentials';

-- API Credentials table
CREATE TABLE IF NOT EXISTS api_credentials (
    user_id TEXT PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    api_provider TEXT NOT NULL DEFAULT 'shinemonitor',
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    api_key TEXT,
    api_secret TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_api_credentials_updated_at
    BEFORE UPDATE ON api_credentials
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
COMMENT ON TABLE api_credentials IS 'Stores credentials for accessing APIs like Shinemonitor, SolisCloud, and Solarman';

-- Plants table
CREATE TABLE IF NOT EXISTS plants (
    plant_id TEXT PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    plant_name TEXT NOT NULL,
    capacity FLOAT8 NOT NULL CHECK (capacity >= 0),
    install_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_plants_updated_at
    BEFORE UPDATE ON plants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
COMMENT ON TABLE plants IS 'Stores solar plant details associated with customers';
CREATE INDEX idx_plants_customer_id ON plants(customer_id);

-- Devices table
CREATE TABLE IF NOT EXISTS devices (
    device_sn TEXT PRIMARY KEY,
    plant_id TEXT NOT NULL REFERENCES plants(plant_id) ON DELETE CASCADE,
    inverter_model TEXT NOT NULL,
    panel_model TEXT NOT NULL,
    pv_count INTEGER NOT NULL CHECK (pv_count >= 0),
    string_count INTEGER NOT NULL CHECK (string_count >= 0),
    first_install_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
COMMENT ON TABLE devices IS 'Stores device details for each plant, typically inverters';
CREATE INDEX idx_devices_plant_id ON devices(plant_id);

-- Device Data Historical table with CHECK constraints
CREATE TABLE IF NOT EXISTS device_data_historical (
    device_sn TEXT NOT NULL REFERENCES devices(device_sn) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    pv01_voltage FLOAT8 NOT NULL CHECK (pv01_voltage >= 0 AND pv01_voltage <= 1000),
    pv01_current FLOAT8 NOT NULL CHECK (pv01_current >= 0 AND pv01_current <= 50),
    pv02_voltage FLOAT8 NOT NULL CHECK (pv02_voltage >= 0 AND pv02_voltage <= 1000),
    pv02_current FLOAT8 NOT NULL CHECK (pv02_current >= 0 AND pv02_current <= 50),
    pv03_voltage FLOAT8 NOT NULL CHECK (pv03_voltage >= 0 AND pv03_voltage <= 1000),
    pv03_current FLOAT8 NOT NULL CHECK (pv03_current >= 0 AND pv03_current <= 50),
    pv04_voltage FLOAT8 NOT NULL CHECK (pv04_voltage >= 0 AND pv04_voltage <= 1000),
    pv04_current FLOAT8 NOT NULL CHECK (pv04_current >= 0 AND pv04_current <= 50),
    pv05_voltage FLOAT8 NOT NULL CHECK (pv05_voltage >= 0 AND pv05_voltage <= 1000),
    pv05_current FLOAT8 NOT NULL CHECK (pv05_current >= 0 AND pv05_current <= 50),
    pv06_voltage FLOAT8 NOT NULL CHECK (pv06_voltage >= 0 AND pv06_voltage <= 1000),
    pv06_current FLOAT8 NOT NULL CHECK (pv06_current >= 0 AND pv06_current <= 50),
    pv07_voltage FLOAT8 NOT NULL CHECK (pv07_voltage >= 0 AND pv07_voltage <= 1000),
    pv07_current FLOAT8 NOT NULL CHECK (pv07_current >= 0 AND pv07_current <= 50),
    pv08_voltage FLOAT8 NOT NULL CHECK (pv08_voltage >= 0 AND pv08_voltage <= 1000),
    pv08_current FLOAT8 NOT NULL CHECK (pv08_current >= 0 AND pv08_current <= 50),
    pv09_voltage FLOAT8 NOT NULL CHECK (pv09_voltage >= 0 AND pv09_voltage <= 1000),
    pv09_current FLOAT8 NOT NULL CHECK (pv09_current >= 0 AND pv09_current <= 50),
    pv10_voltage FLOAT8 NOT NULL CHECK (pv10_voltage >= 0 AND pv10_voltage <= 1000),
    pv10_current FLOAT8 NOT NULL CHECK (pv10_current >= 0 AND pv10_current <= 50),
    pv11_voltage FLOAT8 NOT NULL CHECK (pv11_voltage >= 0 AND pv11_voltage <= 1000),
    pv11_current FLOAT8 NOT NULL CHECK (pv11_current >= 0 AND pv11_current <= 50),
    pv12_voltage FLOAT8 NOT NULL CHECK (pv12_voltage >= 0 AND pv12_voltage <= 1000),
    pv12_current FLOAT8 NOT NULL CHECK (pv12_current >= 0 AND pv12_current <= 50),
    r_voltage FLOAT8 NOT NULL CHECK (r_voltage >= 0 AND r_voltage <= 300),
    s_voltage FLOAT8 NOT NULL CHECK (s_voltage >= 0 AND s_voltage <= 300),
    t_voltage FLOAT8 NOT NULL CHECK (t_voltage >= 0 AND t_voltage <= 300),
    r_current FLOAT8 NOT NULL CHECK (r_current >= 0 AND r_current <= 100),
    s_current FLOAT8 NOT NULL CHECK (s_current >= 0 AND s_current <= 100),
    t_current FLOAT8 NOT NULL CHECK (t_current >= 0 AND t_current <= 100),
    rs_voltage FLOAT8 NOT NULL CHECK (rs_voltage >= 0),
    st_voltage FLOAT8 NOT NULL CHECK (st_voltage >= 0),
    tr_voltage FLOAT8 NOT NULL CHECK (tr_voltage >= 0),
    frequency FLOAT8 NOT NULL CHECK (frequency >= 0),
    total_power FLOAT8 NOT NULL CHECK (total_power >= 0 AND total_power <= 100000),
    reactive_power FLOAT8 NOT NULL CHECK (reactive_power >= 0),
    energy_today FLOAT8 NOT NULL CHECK (energy_today >= 0 AND energy_today <= 1000),
    cuf FLOAT8 NOT NULL CHECK (cuf >= 0),
    pr FLOAT8 NOT NULL CHECK (pr >= 0 AND pr <= 100),
    state TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (device_sn, timestamp)
);
CREATE TRIGGER update_device_data_historical_updated_at
    BEFORE UPDATE ON device_data_historical
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
COMMENT ON TABLE device_data_historical IS 'Stores historical data for devices with CHECK constraints for valid ranges';
CREATE INDEX idx_device_data_historical_device_sn ON device_data_historical(device_sn);
CREATE INDEX idx_device_data_historical_timestamp ON device_data_historical(timestamp);
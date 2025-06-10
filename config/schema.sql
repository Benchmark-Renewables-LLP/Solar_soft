-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Plants table
CREATE TABLE IF NOT EXISTS plants (
    plant_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255),
    capacity FLOAT,  -- in kW
    total_energy FLOAT,  -- in kWh
    install_date DATE,
    latitude FLOAT,
    longitude FLOAT
);

-- Devices table
CREATE TABLE IF NOT EXISTS devices (
    sn TEXT PRIMARY KEY,
    plant_id INTEGER REFERENCES plants(plant_id),
    first_install_date DATE,
    inverter_model VARCHAR(100),
    panel_model VARCHAR(100),
    pv_count INTEGER,
    string_count INTEGER
);

-- Device current data (5-minute intervals)
CREATE TABLE IF NOT EXISTS device_data_current (
    device_id TEXT REFERENCES devices(sn),
    timestamp TIMESTAMPTZ NOT NULL,
    pv01_voltage FLOAT,
    pv01_current FLOAT,
    pv02_voltage FLOAT,
    pv02_current FLOAT,
    pv03_voltage FLOAT,
    pv03_current FLOAT,
    pv04_voltage FLOAT,
    pv04_current FLOAT,
    pv05_voltage FLOAT,
    pv05_current FLOAT,
    pv06_voltage FLOAT,
    pv06_current FLOAT,
    pv07_voltage FLOAT,
    pv07_current FLOAT,
    pv08_voltage FLOAT,
    pv08_current FLOAT,
    pv09_voltage FLOAT,
    pv09_current FLOAT,
    pv10_voltage FLOAT,
    pv10_current FLOAT,
    pv11_voltage FLOAT,
    pv11_current FLOAT,
    pv12_voltage FLOAT,
    pv12_current FLOAT,
    r_voltage FLOAT,
    s_voltage FLOAT,
    t_voltage FLOAT,
    r_current FLOAT,
    s_current FLOAT,
    t_current FLOAT,
    rs_voltage FLOAT,
    st_voltage FLOAT,
    tr_voltage FLOAT,
    frequency FLOAT,
    total_power FLOAT,
    reactive_power FLOAT,
    energy_today FLOAT,
    cuf FLOAT,
    pr FLOAT,
    state TEXT,
    PRIMARY KEY (device_id, timestamp)
);

SELECT create_hypertable('device_data_current', 'timestamp', if_not_exists => true);

-- Device daily historical data
CREATE TABLE IF NOT EXISTS device_daily_historical (
    device_id TEXT REFERENCES devices(sn),
    date DATE NOT NULL,
    avg_pv01_voltage FLOAT,
    avg_pv01_current FLOAT,
    avg_pv02_voltage FLOAT,
    avg_pv02_current FLOAT,
    avg_pv03_voltage FLOAT,
    avg_pv03_current FLOAT,
    avg_pv04_voltage FLOAT,
    avg_pv04_current FLOAT,
    avg_pv05_voltage FLOAT,
    avg_pv05_current FLOAT,
    avg_pv06_voltage FLOAT,
    avg_pv06_current FLOAT,
    avg_pv07_voltage FLOAT,
    avg_pv07_current FLOAT,
    avg_pv08_voltage FLOAT,
    avg_pv08_current FLOAT,
    avg_pv09_voltage FLOAT,
    avg_pv09_current FLOAT,
    avg_pv10_voltage FLOAT,
    avg_pv10_current FLOAT,
    avg_pv11_voltage FLOAT,
    avg_pv11_current FLOAT,
    avg_pv12_voltage FLOAT,
    avg_pv12_current FLOAT,
    avg_r_voltage FLOAT,
    avg_s_voltage FLOAT,
    avg_t_voltage FLOAT,
    avg_r_current FLOAT,
    avg_s_current FLOAT,
    avg_t_current FLOAT,
    avg_rs_voltage FLOAT,
    avg_st_voltage FLOAT,
    avg_tr_voltage FLOAT,
    avg_frequency FLOAT,
    avg_total_power FLOAT,
    avg_reactive_power FLOAT,
    avg_energy_today FLOAT,
    avg_cuf FLOAT,
    avg_pr FLOAT,
    state TEXT,
    PRIMARY KEY (device_id, date)
);

SELECT create_hypertable('device_daily_historical', 'date', if_not_exists => true);

-- Weather data table
CREATE TABLE IF NOT EXISTS weather_data (
    plant_id INTEGER REFERENCES plants(plant_id),
    timestamp TIMESTAMPTZ NOT NULL,
    irradiance FLOAT,  -- W/m²
    temperature FLOAT,  -- °C
    cloud_cover FLOAT,  -- Percentage
    PRIMARY KEY (plant_id, timestamp)
);

SELECT create_hypertable('weather_data', 'timestamp', if_not_exists => true);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    plant_id INTEGER REFERENCES plants(plant_id),
    device_id TEXT REFERENCES devices(sn),
    timestamp TIMESTAMPTZ NOT NULL,
    alert_type TEXT,
    message TEXT,
    severity TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (device_id, timestamp)
);

SELECT create_hypertable('alerts', 'timestamp', if_not_exists => true);
# Schema Design

## Objective
Design the database schema for the SolarMonitoring project, supporting a two-layered structure (admin and customer), paying customer features, and admin features.

## Schema Details
- `users`: Stores user credentials and roles for authentication.
  - `user_id` (PK)
  - `username` (TEXT, UNIQUE)
  - `password` (TEXT, hashed)
  - `role` (ENUM: 'admin', 'customer')
  - `customer_id` (FOREIGN KEY, nullable)
  - `is_paying` (BOOLEAN)
- `customers`: Stores customer metadata.
  - `customer_id` (PK)
  - `customer_name` (TEXT)
  - `api_type` (TEXT)
  - `api_credentials` (JSONB)
  - `location` (TEXT)
- `plants`: Stores plant metadata linked to customers.
  - `plant_id` (PK)
  - `customer_id` (FOREIGN KEY)
  - `user_id` (FOREIGN KEY)
  - `capacity` (FLOAT)
  - `total_energy` (FLOAT)
- `devices`: Stores device metadata with inverter and panel models.
  - `device_id` (PK)
  - `plant_id` (FOREIGN KEY)
  - `first_install_date` (DATE)
  - `pn`, `devcode`, `devaddr`, `pv_count`, `string_count` (metadata)
  - `inverter_model`, `panel_model` (TEXT)
- `device_daily_historical`: Stores daily averaged data.
  - `device_id` (FOREIGN KEY)
  - `date` (DATE)
  - Averaged metrics (e.g., `avg_pv01_voltage`, `avg_total_power`)
  - Hypertable on `date`
- `device_data_current`: Stores current day time-series data.
  - `device_id` (FOREIGN KEY)
  - `timestamp` (TIMESTAMPTZ)
  - Metrics (e.g., `pv01_voltage`, `total_power`)
  - Hypertable on `timestamp`
- `error_history`: Logs errors.
  - `id` (PK)
  - `user_id`, `plant_id`, `device_id`, `timestamp`, `action`, `error_code`, `error_description`
- `device_analysis`: Stores analysis results.
  - `device_id` (FOREIGN KEY)
  - `date` (DATE)
  - `avg_pr`, `avg_total_power`, `pr_threshold_flag`, `power_degradation_flag`, `fault_count`, `z_score_power`, `generation_per_kw`, `efficiency`

## Learning Resources
- [TimescaleDB Documentation](https://docs.timescale.com/): Learn how to create hypertables for time-series data.
- [PostgreSQL Documentation](https://www.postgresql.org/docs/): Understand table creation, constraints, and JSONB for storing API credentials.
- [Role-Based Access Control](https://www.okta.com/identity-101/role-based-access-control/): Guide to implementing RBAC in database design.
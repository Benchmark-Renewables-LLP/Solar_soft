# Project Setup

## Objective
Set up the directory structure and initial configuration files for the SolarMonitoring project.

## Directory Structure
- `SolarMonitoring/`: Root directory.
  - `Dockerfile`: For the Flask API and ingestion scripts.
  - `schema.sql`: Database schema.
  - `requirements.txt`: Python dependencies.
  - `config/`: Configuration files.
    - `.env`: Environment variables.
    - `docker-compose.yml`: Docker services.
    - `settings.py`: Load environment variables.
  - `backend/`: Backend scripts and API.
    - `api/`: Flask API.
    - `data/`: Input data (e.g., `users.csv`).
    - `scripts/`: Ingestion and analysis scripts.
  - `frontend/`: React app (pre-built "Lovable" dashboard).
  - `docs/`: Documentation.

## Files Created
- `requirements.txt`: Lists Python dependencies for the backend.
  - Flask: For the REST API.
  - psycopg2-binary: For TimescaleDB connection.
  - requests: For Shinemonitor API calls.
  - python-dotenv: For loading environment variables.
  - bcrypt: For password hashing.
  - PyJWT: For JWT authentication.

## Learning Resources
- [Flask Documentation](https://flask.palletsprojects.com/en/2.3.x/): Learn how to build a REST API with Flask.
- [Psycopg2 Documentation](https://www.psycopg.org/docs/): Understand how to connect to PostgreSQL/TimescaleDB.
- [Python-dotenv Documentation](https://pypi.org/project/python-dotenv/): Guide to loading environment variables.
- [PyJWT Documentation](https://pyjwt.readthedocs.io/en/stable/): Learn about JWT for authentication.
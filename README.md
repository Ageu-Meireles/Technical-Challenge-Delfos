# Delfos - ETL Pipeline Documentation

## Overview

This project implements a complete ETL (Extract, Transform, Load) pipeline with microservices architecture, using FastAPI for the data API, PostgreSQL for storage, and an ETL process for data aggregation.

## Architecture


![Architecture](./images/architecture.svg)


## Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- make (for local development)

## Initial Setup

### 1. Environment Variables

Copy the example file and configure the variables:

```bash
cp .env.example .env
```

The `.env` file contains the default configurations of the source and target databases, as well as routes for accessing the API and databases through scripts.

### 2. Start Infrastructure

```bash
docker compose up --build -d
```

This command will:
- Create and start two PostgreSQL databases, source and target, building the entire target database structure beforehand based on a snapshot with previously applied migrations.
- Build and start the FastAPI API (ensuring application of source database migrations and populating random data starting from 01/01/2025 with a 10-day interval)
- Build and start the Dagster service (optional)

## Accessing Services

### FastAPI API

- **URL**: http://localhost:8000
- **Swagger Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **ReDoc**: http://localhost:8000/redoc

The API routes and endpoints are properly documented in the Swagger UI accessible at /docs.

### Databases

#### Source Database (raw data)
- **Host**: localhost
- **Port**: 5433
- **Database**: delfos
- **User**: delfos
- **Password**: delfos

#### Target Database (aggregated data)
- **Host**: localhost
- **Port**: 5434
- **Database**: delfos
- **User**: delfos
- **Password**: delfos

### Dagster (optional)
- **URL**: http://localhost:3000

## ETL Process

### Data Structure

#### Source Database (raw data)
- **Frequency**: 1 minute
- **Period**: 10 consecutive days (2025-01-01 to 2025-01-10)
- **Table**: `data`

#### Target Database (aggregated data)
- **Frequency**: 10 minutes
- **Aggregations**: mean, min, max, std
- **Tables**: `signal` and `data`

### Running ETL Manually

#### Via Docker

```bash
docker compose exec dagster python -m src.main 2025-01-02
```

#### Local (if you have dependencies installed)

```bash
cd etl
python -m src.main 2025-01-02
```

### What does the ETL do?

1. **Extract**: Queries the API to get data from a specific day
2. **Transform**: Aggregates data in 10-minute windows with statistics
3. **Load**: Inserts aggregated data into the target database

**Example of created aggregations:**
- `wind_speed_mean` - Mean of wind speed
- `wind_speed_min` - Minimum of wind speed
- `wind_speed_max` - Maximum of wind speed
- `wind_speed_std` - Standard deviation of wind speed
- `power_mean` - Mean of power
- `power_min` - Minimum of power
- `power_max` - Maximum of power
- `power_std` - Standard deviation of power

## Useful Commands

### Docker

```bash
# Check container status
docker compose ps

# Check logs
docker compose logs -f api
docker compose logs -f dagster

# Stop services
docker compose down

# Rebuild and start
docker compose up --build -d
```
## Usage Examples

### 1. Check if API is working

```bash
curl http://localhost:8000/health
```

### 2. Get data from the first day

```bash
curl "http://localhost:8000/data?start=2025-01-01T00:00:00&end=2025-01-01T23:59:59"
```

### 3. Get only wind_speed and power

```bash
curl "http://localhost:8000/data?start=2025-01-01T00:00:00&end=2025-01-01T01:00:00&variables=wind_speed,power"
```

### 4. Run ETL for a specific day

```bash
docker compose exec dagster python -m src.main 2025-01-01
```

### 5. Check aggregated data in target database

```bash
docker compose exec target_db psql -U delfos -d delfos -c "
SELECT d.timestamp, s.name, d.value 
FROM data d 
JOIN signal s ON d.signal_id = s.id 
WHERE d.timestamp >= '2025-01-01' AND d.timestamp < '2025-01-02'
ORDER BY d.timestamp, s.name
LIMIT 20;"
```

## Project Structure

```
delfos/
├── api/                    # FastAPI application
│   ├── src/
│   │   ├── core/          # Configurations and utilities
│   │   ├── db/            # Models and database connection
│   │   ├── routes/        # API endpoints
│   │   └── main.py        # FastAPI application
│   ├── scripts/           # Seed scripts
│   ├── tests/             # Tests
│   └── Dockerfile
├── etl/                    # ETL process
│   ├── src/
│   │   ├── core/          # Configurations
│   │   ├── db/            # Models and connection
│   │   ├── orchestration/ # Dagster assets
│   │   └── main.py        # Main ETL script
│   ├── tests/             # Tests
│   └── Dockerfile
├── .env.example           # Example environment variables
├── docker-compose.yaml    # Service orchestration
└── README.md             # This file
```

## Troubleshooting

### Common Problems

1. **Ports already in use**
   ```bash
   # Check which processes are using the ports
   lsof -i :5433
   lsof -i :5434
   lsof -i :8000
   
   # Stop services and try again
   docker compose down
   docker compose up --build -d
   ```

2. **API doesn't respond**
   ```bash
   # Check API logs
   docker compose logs api
   
   # Check if container is running
   docker compose ps
   ```

3. **ETL fails**
   ```bash
   # Check ETL logs
   docker compose logs dagster
   
   # Check if API is accessible from ETL container
   docker compose exec dagster curl http://api:8000/health
   ```

4. **Database doesn't connect**
   ```bash
   # Check if databases are running
   docker compose ps source_db target_db
   
   # Test connection
   docker compose exec source_db psql -U delfos -d delfos -c "SELECT 1;"
   docker compose exec target_db psql -U delfos -d delfos -c "SELECT 1;"
   ```

### Logs and Monitoring

```bash
# View all logs in real time
docker compose logs -f

# Logs from a specific service
docker compose logs -f api
docker compose logs -f dagster
docker compose logs -f source_db
docker compose logs -f target_db
```

## Development

### Running Locally (without Docker)

If you prefer to run services locally for development:

1. **Install dependencies**
>Assuming poetry is already installed, create a virtual environment for each:

```bash
cd api && poetry install
cd ../etl && poetry install
```

2. **Configure local PostgreSQL databases** on ports 5433 and 5434

3. **Create migrations automatically**

```bash
# inside the 'api' or 'etl' directory
make db-migrate
```

4. **Run migrations**

```bash
# inside the 'api' or 'etl' directory
make db-migrate
```

5. **Start API**
```bash
   cd api && make run-dev
```

6. **Run ETL**
```bash
   cd etl && python -m src.main 2025-01-01
```

### Tests

```bash
# inside the 'api' or 'etl' directory
make test
```

## Design Decisions
> some choices were made based on the requirements of the test, such as the choice of FastAPI as the tool for the API, the use of a relational database like PostgreSQL, and so forth.

* **FastAPI**: modern, fast, and strongly typed
* **SQLModel**: clean integration of SQLAlchemy and Pydantic
* **httpx**: async-ready HTTP client
* **pandas**: efficient time-series aggregation
* **PostgreSQL**: reliable relational storage
* **Dagster (optional)**: production-grade orchestration

## Notes

This repository contains **all design decisions and execution instructions** required to understand, run, and evaluate the project.

## License

This project was developed as part of a technical assessment.

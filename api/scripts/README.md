# Database Seed Script

This script populates the database with sample data for testing and development purposes.

## Usage

### Via Makefile (Recommended)

```bash
# Use default values (2025-01-01, 10 days)
make seeds

# Specify custom start date
make seeds ARGS="--start-date 2025-02-01"

# Specify custom number of days
make seeds ARGS="--days 5"

# Both parameters
make seeds ARGS="--start-date 2025-02-01 --days 7"

# Show help
make seeds ARGS="--help"
```

### Direct Execution


```bash
# Run from api directory
PYTHONPATH=. python3 scripts/seed.py

# Use default values
python3 scripts/seed.py

# Specify custom parameters
python3 scripts/seed.py --start-date 2025-02-01 --days 5

# Show help
python3 scripts/seed.py --help
```

## Parameters

- `--start-date`: Start date in YYYY-MM-DD format (default: 2025-01-01)
- `--days`: Number of days to generate data for (default: 10)
- `--help`: Show available options

## Features

- **Duplicate Prevention**: Checks for existing records before insertion to avoid duplicates
- **Configurable Time Range**: Generate data for any date range and duration
- **High Frequency Data**: Creates 1-minute interval data (1440 records per day)
- **Logging**: Informative output showing progress and data range

## Generated Data

The script generates data including:

- **Timestamp**: 1-minute intervals
- **Wind Speed**: Normal distribution (mean: 6.0 m/s, std: 1.5 m/s)
- **Power Output**: Random values within realistic bounds
- **Ambient Temperature**: Normal distribution (mean: 25.0°C, std: 3.0°C)

## Examples

### Generate 3 days of data starting from February 1st, 2025:
```bash
make seeds ARGS="--start-date 2025-02-01 --days 3"
```

Output:
```
INFO - Generated 4320 records for validation.
INFO - Inserting 4320 rows...
INFO - Seed completed successfully.
INFO - Data range: 2025-02-01 00:00:00 → 2025-02-03 23:59:00
```

### Using defaults:
```bash
make seeds
```

Output:
```
INFO - Using default start date: 2025-01-01
INFO - Using default number of days: 10
INFO - Generated 14400 records for validation.
INFO - Inserting 14400 rows...
INFO - Seed completed successfully.
INFO - Data range: 2025-01-01 00:00:00 → 2025-01-10 23:59:00
```

### When data already exists:
```
INFO - Using default start date: 2025-01-01
INFO - Using default number of days: 10
INFO - Generated 14400 records for validation.
INFO - All records already exist in the database. No insertion needed.
```

## Notes

- The script requires database connection settings configured in `src/core/settings.py`
- Each day generates 1,440 records (24 hours × 60 minutes)
- The script is safe to run multiple times - it will skip existing records
- Database transactions are used to ensure data integrity

from datetime import datetime
import argparse
from typing import List
import logging

import numpy as np
import pandas as pd
from sqlmodel import select
from src.db import get_session
from src.db.models import Data
from contextlib import contextmanager

from src.core import settings

settings.source_db_url = ""

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -------------------------------
# SEED CONFIGURATION
# -------------------------------
DEFAULT_START_DATE = datetime(2025, 1, 1, 0, 0, 0)
DEFAULT_DAYS = 10
FREQUENCY = "1min"
RANDOM_SEED = 42

get_db_session = contextmanager(get_session)

def generate_data(start_date: datetime = DEFAULT_START_DATE, days: int = DEFAULT_DAYS) -> pd.DataFrame:
    np.random.seed(RANDOM_SEED)

    timestamps = pd.date_range(
        start=start_date,
        periods=days * 24 * 60,
        freq=FREQUENCY,
    )

    wind_speed = np.random.normal(
        loc=6.0,     # average wind speed
        scale=1.5,   # variability
        size=len(timestamps),
    ).clip(min=0)

    power = (
        wind_speed ** 3
        + np.random.normal(0, 50, len(timestamps))
    ).clip(min=0)

    ambient_temperature = np.random.normal(
        loc=25.0,
        scale=3.0,
        size=len(timestamps),
    )

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "wind_speed": wind_speed,
            "power": power,
            "ambient_temperature": ambient_temperature,
        }
    )


def check_existing_records(timestamps: List[datetime]) -> List[datetime]:
    """Check which timestamps already exist in the database."""
    with get_db_session() as session:
        statement = select(Data.timestamp).where(Data.timestamp.in_(timestamps))
        existing = session.exec(statement).all()
        return existing


def seed_database(start_date: datetime, days: int):
    df = generate_data(start_date, days)
    logger.info(f"Generated {len(df)} records for validation.")
    
    timestamps = df["timestamp"].tolist()
    existing_timestamps = check_existing_records(timestamps)
    
    if existing_timestamps:
        # Filter out existing records
        existing_set = set(existing_timestamps)
        df = df[~df["timestamp"].isin(existing_set)]
        
        if len(df) == 0:
            logger.info("All records already exist in the database. No insertion needed.")
            return
        
        logger.info(f"Found {len(existing_timestamps)} existing records. Inserting {len(df)} new records...")
    else:
        logger.info(f"Inserting {len(df)} rows...")
    records = [
        Data(
            timestamp=row.timestamp.to_pydatetime(),
            wind_speed=float(row.wind_speed),
            power=float(row.power),
            ambient_temperature=float(row.ambient_temperature),
        )
        for row in df.itertuples(index=False)
    ]

    with get_db_session() as session:
        session.bulk_save_objects(records)
        session.commit()

    logger.info("Seed completed successfully.")
    logger.info(
        f"Data range: {df.timestamp.min()} → {df.timestamp.max()}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database with sample data")
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date in YYYY-MM-DD format (default: 2025-01-01)",
        default="2025-01-01"
    )
    parser.add_argument(
        "--days",
        type=int,
        help="Number of days to generate data for (default: 10)",
        default=10
    )
    
    args = parser.parse_args()
    
    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    except ValueError:
        logger.error("Invalid date format. Use YYYY-MM-DD")
        exit(1)
    
    if args.start_date == "2025-01-01" and args.days == 10:
        logger.info(f"Using default start date: {start_date.strftime('%Y-%m-%d')}")
        logger.info(f"Using default number of days: {args.days}")
    
    seed_database(start_date=start_date, days=args.days)

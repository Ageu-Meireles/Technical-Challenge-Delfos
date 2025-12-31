import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, Iterable, Optional

import httpx
import pandas as pd
from sqlmodel import Session, select
from sqlalchemy.engine import Engine

from src.db import engine as default_engine
from src.db.models import Signal, Data
from src.core import settings

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AGGREGATIONS = ["mean", "min", "max", "std"]
VARIABLES = ["wind_speed", "power"]

def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format")

def fetch_source_data(
    date: datetime,
    client: Optional[httpx.Client] = None,
    variables: Iterable[str] = VARIABLES,
) -> pd.DataFrame:
    start = date
    end = date + timedelta(days=1) - timedelta(seconds=1)

    params = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "variables": list(variables),
    }

    close_client = False
    if client is None:
        client = httpx.Client(
            base_url=settings.source_api_url,
            timeout=30,
        )
        close_client = True

    try:
        response = client.get("/data", params=params)
        response.raise_for_status()
    finally:
        if close_client:
            client.close()

    df = pd.DataFrame(response.json())

    if df.empty:
        raise RuntimeError("No data returned from source API")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    return df

def aggregate_data(df: pd.DataFrame) -> pd.DataFrame:
    aggregated = (
        df
        .resample("10min")
        .agg(AGGREGATIONS)
    )

    aggregated.columns = [
        f"{var}_{agg}"
        for var, agg in aggregated.columns
    ]

    return aggregated

def ensure_signals(
    session: Session,
    variables: Iterable[str] = VARIABLES,
    aggregations: Iterable[str] = AGGREGATIONS,
) -> Dict[str, int]:
    signal_map: Dict[str, int] = {}

    existing = {
        signal.name: signal
        for signal in session.exec(select(Signal)).all()
    }

    for variable in variables:
        for agg in aggregations:
            name = f"{variable}_{agg}"

            if name not in existing:
                signal = Signal(name=name)
                session.add(signal)
                session.commit()
                session.refresh(signal)
            else:
                signal = existing[name]

            signal_map[name] = signal.id

    return signal_map


def load_data(
    session: Session,
    aggregated: pd.DataFrame,
    signal_map: Dict[str, int],
):
    records = []

    for timestamp, row in aggregated.iterrows():
        for signal_name, value in row.items():
            if pd.isna(value):
                continue

            signal_id = signal_map[signal_name]
            
            # Check if record already exists
            existing = session.exec(
                select(Data).where(
                    Data.timestamp == timestamp,
                    Data.signal_id == signal_id
                )
            ).first()
            
            if existing is None:
                records.append(
                    Data(
                        timestamp=timestamp,
                        signal_id=signal_id,
                        value=float(value),
                    )
                )

    if records:
        session.bulk_save_objects(records)
        session.commit()

def run_etl(
    date_str: str,
    *,
    engine: Engine = default_engine,
    api_client: Optional[httpx.Client] = None,
):
    date = parse_date(date_str)

    logger.info("Running ETL for date %s", date.date())

    df = fetch_source_data(date, client=api_client)
    aggregated = aggregate_data(df)

    with Session(engine) as session:
        signal_map = ensure_signals(session)
        load_data(session, aggregated, signal_map)

    logger.info("ETL completed successfully for %s", date.date())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.main YYYY-MM-DD")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    run_etl(sys.argv[1])

from dagster import resource
import httpx
from sqlalchemy import create_engine
from src.core import settings

@resource
def source_api():
    return httpx.Client(
        base_url=settings.source_api_url,
        timeout=30,
    )

@resource
def target_db():
    engine = create_engine(settings.target_db_url)
    return engine
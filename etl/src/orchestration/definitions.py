from dagster import Definitions
from src.orchestration.assets import daily_etl
from src.orchestration.resources import source_api, target_db
from src.orchestration.schedules import daily_schedule, daily_etl_job

defs = Definitions(
    assets=[daily_etl],
    jobs=[daily_etl_job],
    resources={
        "source_api": source_api,
        "target_db": target_db,
    },
    schedules=[daily_schedule],
)
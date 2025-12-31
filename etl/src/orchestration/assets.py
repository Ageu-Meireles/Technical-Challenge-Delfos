from dagster import asset, DailyPartitionsDefinition
from src.main import run_etl

daily_partitions = DailyPartitionsDefinition(start_date="2025-01-01")

@asset(partitions_def=daily_partitions, required_resource_keys={"source_api", "target_db"})
def daily_etl(context):
    partition_date = context.partition_key

    context.log.info(f"Running ETL for {partition_date}")

    run_etl(
        date_str=partition_date,
        api_client=context.resources.source_api,
        engine=context.resources.target_db,
    )
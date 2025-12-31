from dagster import ScheduleDefinition, define_asset_job

daily_etl_job = define_asset_job("daily_etl_job", ["daily_etl"])

daily_schedule = ScheduleDefinition(
    job=daily_etl_job,
    cron_schedule="0 1 * * *",  # todo dia 01:00
)
db-migrations:
	alembic revision --autogenerate -m "$(MESSAGE)"

db-migrate:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

run-dev:
	fastapi run src/main.py

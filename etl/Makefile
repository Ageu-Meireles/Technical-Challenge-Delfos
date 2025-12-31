test:
	pytest

db-migrations:
	alembic revision --autogenerate -m "$(MESSAGE)"

db-migrate:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

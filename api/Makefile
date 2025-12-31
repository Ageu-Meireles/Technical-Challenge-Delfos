test:
	pytest

db-migrations:
	alembic revision --autogenerate -m "$(MESSAGE)"

db-migrate:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

run-dev:
	fastapi run src/main.py

seeds:
	PYTHONPATH=. python3 scripts/seed.py $(ARGS)
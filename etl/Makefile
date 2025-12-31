@all: format lint test

format:
	black .
	isort .

lint:
	flake8 .

test:
	pytest

db-migrations:
	alembic revision --autogenerate -m "$(MESSAGE)"

db-migrate:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

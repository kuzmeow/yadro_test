# COMMON
install:
	uv sync

lint:
	uv run pre-commit run --all


# DEV
install_dev:
	uv sync --all-extras
	uv run pre-commit install

run:
	uv run app

run_all:
	docker compose up postgres redis -d
	$(MAKE) run
	$(MAKE) run_taskiq

run_docker:
	docker compose up -b

create_migration:
	@read -p "Введите описание ревизии: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

shell_create_migration:
	@powershell -Command "uv run alembic revision --autogenerate -m '$(msg)'"

migrate:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1

run_taskiq:
	uv run taskiq worker notification_service.infra.taskiq.taskiq_broker:broker notification_service.infra.taskiq.tasks

test:
	export ENV_FOR_DYNACONF=test; uv run pytest

shell_test:
	@set ENV_FOR_DYNACONF=test && uv run pytest -l

test_cov:
	export ENV_FOR_DYNACONF=test; uv run pytest --cov

shell_test_cov:
	@set ENV_FOR_DYNACONF=test && uv run pytest --cov

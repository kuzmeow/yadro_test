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

run_taskiq:
	uv run taskiq worker notification_service.infra.taskiq.taskiq_broker:broker notification_service.infra.taskiq.tasks

run_all:
	docker compose up postgres redis -d
	$(MAKE) migrate
	$(MAKE) run

run_docker_all:
	docker compose up --build

run_docker_back:
	docker compose up notification-service taskiq --build

create_migration:
	@read -p "Введите описание ревизии: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

shell_create_migration:
	@powershell -Command "uv run alembic revision --autogenerate -m '$(msg)'"

migrate:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1


test:
	export ENV_FOR_DYNACONF=test; uv run pytest

shell_test:
	@set ENV_FOR_DYNACONF=test && uv run pytest -l

test_cov:
	export ENV_FOR_DYNACONF=test; uv run pytest --cov

shell_test_cov:
	@set ENV_FOR_DYNACONF=test && uv run pytest --cov

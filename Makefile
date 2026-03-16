COMPOSE = docker compose
SERVICE = assetsvc
SERVICE_TEST = assetsvc-test
DATA = asset_data_1000_valid.json

.PHONY: help build up down restart logs test load shell clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the docker images
	$(COMPOSE) build

up: ## Start the asset service
	$(COMPOSE) up -d

down: ## Stop and remove containers
	$(COMPOSE) down

restart: down up ## Restart the service

logs: ## Show service logs
	$(COMPOSE) logs -f $(SERVICE)

test: ## Run test suite
	$(COMPOSE) --profile test run --rm $(SERVICE) pytest

migrate: ## Apply database migrations
	$(COMPOSE) run --rm $(SERVICE) alembic upgrade head

load: migrate ## Load database with json
	$(COMPOSE) run --rm \
	-v $(shell pwd)/sample_data/$(DATA):/app/$(DATA) \
 	$(SERVICE) cli load $(DATA)

shell: ## Enter shell for asset service
	$(COMPOSE) exec $(SERVICE) /bin/bash

clean: ## Remove volumes and reset db
	$(COMPOSE) down -v

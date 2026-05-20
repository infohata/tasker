.PHONY: help up down build rebuild shell test migrate makemigrations manage collectstatic logs ps clean self-sweep

DC := docker compose

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

up: ## Start the stack (web, db, redis, nginx) in detached mode
	$(DC) up -d

down: ## Stop the stack and remove containers (volumes preserved)
	$(DC) down

build: ## Rebuild the web image
	$(DC) build web

rebuild: ## Stop, rebuild, and restart the web service
	$(DC) down
	$(DC) build web
	$(DC) up -d

shell: ## Open a bash shell in the web container
	$(DC) exec web bash

test: ## Run pytest inside the web container
	$(DC) exec -T web pytest

migrate: ## Apply Django migrations
	$(DC) exec web python manage.py migrate

makemigrations: ## Create migrations from model changes
	$(DC) exec web python manage.py makemigrations

manage: ## Run a manage.py subcommand: make manage ARGS="shell" (or createsuperuser, dbshell, …)
	$(DC) exec web python manage.py $(ARGS)

collectstatic: ## Collect static files into static_collected/ (served by nginx)
	$(DC) exec -T web python manage.py collectstatic --noinput

logs: ## Tail logs for all services
	$(DC) logs -f

ps: ## Show running services
	$(DC) ps

self-sweep: ## Run pyflakes against project source (RULE_self-sweep-before-push)
	$(DC) exec -T web python -m pyflakes tasker_django tasker

clean: ## Stop the stack and drop named volumes (DESTRUCTIVE — wipes DB)
	$(DC) down -v

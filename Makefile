.PHONY: up down build logs shell psql reset test lint help

# ── Variables ────────────────────────────────────────────────
COMPOSE = docker compose
BACKEND = $(COMPOSE) exec backend
PSQL    = $(COMPOSE) exec postgres psql -U phantom

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Docker ───────────────────────────────────────────────────
up: ## Start all services (build if needed)
	$(COMPOSE) up -d --build
	@echo "\n✅ PHANTOM is running at http://localhost:3000"
	@echo "   API docs: http://localhost:8000/docs"

down: ## Stop all services
	$(COMPOSE) down

build: ## Force rebuild all images
	$(COMPOSE) build --no-cache

logs: ## Follow logs from all services
	$(COMPOSE) logs -f

logs-backend: ## Follow backend logs only
	$(COMPOSE) logs -f backend

logs-frontend: ## Follow frontend logs only
	$(COMPOSE) logs -f frontend

# ── Development ──────────────────────────────────────────────
shell: ## Open shell in backend container
	$(BACKEND) /bin/bash

psql: ## Open PostgreSQL interactive shell
	$(PSQL)

reset: ## Wipe database and restart (DESTRUCTIVE)
	$(COMPOSE) down -v
	$(COMPOSE) up -d --build
	@echo "⚠️  Database wiped and services restarted"

migrate: ## Run database migrations (Alembic)
	$(BACKEND) alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MSG="add users table")
	$(BACKEND) alembic revision --autogenerate -m "$(MSG)"

# ── Testing ──────────────────────────────────────────────────
test: ## Run all backend tests
	$(BACKEND) pytest tests/ -v --tb=short

test-watch: ## Run tests in watch mode
	$(BACKEND) ptw tests/ --tb=short

lint: ## Run linters (ruff + mypy)
	$(BACKEND) ruff check app/
	$(BACKEND) mypy app/

# ── Status ───────────────────────────────────────────────────
status: ## Show container status
	$(COMPOSE) ps

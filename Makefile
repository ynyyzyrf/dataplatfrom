# GeneralDataPlatform - Dev Commands

.PHONY: help backend-run backend-test frontend-dev db-up db-down lint format setup

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# -- Backend -------------------------------------------------------------

backend-install: ## Install backend Python dependencies
	cd backend && pip install -r requirements-dev.txt

backend-run: ## Start FastAPI in dev mode (hot-reload)
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-test: ## Run backend tests
	cd backend && python -m pytest tests/ -v

backend-migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

backend-migration: ## Create a new Alembic migration
	cd backend && alembic revision --autogenerate -m "$(message)"

# -- Frontend ------------------------------------------------------------

frontend-install: ## Install frontend dependencies
	cd frontend && npm install

frontend-dev: ## Start frontend dev server
	cd frontend && npm run dev

frontend-build: ## Build frontend for production
	cd frontend && npm run build

# -- Docker --------------------------------------------------------------

db-up: ## Start Docker services (PostgreSQL, Redis, etc.)
	docker compose up -d postgres redis minio

db-down: ## Stop Docker services
	docker compose down

all-up: ## Start all Docker services
	docker compose up -d

all-down: ## Stop all Docker services
	docker compose down

# -- Quality -------------------------------------------------------------

lint: ## Run Python linting
	cd backend && ruff check .

format: ## Run Python formatting
	cd backend && ruff format .

lint-frontend: ## Run frontend linting
	cd frontend && npx eslint src/

# -- Project -------------------------------------------------------------

setup: ## Full project setup (backend + frontend)
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install
	docker compose up -d postgres redis
	cd backend && alembic upgrade head
	@echo "Setup complete!"

# ============================================================
# Athletic AI — Makefile
# ============================================================

.PHONY: help up down logs shell-api test-backend test-frontend seed migrate lint

help:
	@echo "Athletic AI — Comandos disponíveis:"
	@echo "  make up           → Sobe todos os serviços"
	@echo "  make down         → Para todos os serviços"
	@echo "  make down-v       → Para e remove volumes (banco zerado)"
	@echo "  make logs         → Logs em tempo real"
	@echo "  make shell-api    → Shell no container da API"
	@echo "  make migrate      → Roda migrations Alembic"
	@echo "  make seed         → Popula banco com dados demo"
	@echo "  make test-backend → Roda testes do backend"
	@echo "  make test-frontend→ Roda testes do frontend"
	@echo "  make lint         → Roda linters (ruff + eslint)"

up:
	docker compose up -d

down:
	docker compose down

down-v:
	docker compose down -v

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

shell-api:
	docker compose exec api bash

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python scripts/seed.py

test-backend:
	docker compose exec api pytest tests/ -v --cov=app --cov-report=term-missing

test-frontend:
	docker compose exec frontend npm run test

lint:
	docker compose exec api ruff check app/
	docker compose exec api black --check app/
	docker compose exec frontend npm run lint

format:
	docker compose exec api ruff check --fix app/
	docker compose exec api black app/

build:
	docker compose build --no-cache

restart-api:
	docker compose restart api

ps:
	docker compose ps

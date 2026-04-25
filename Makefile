# ============================================================
# MENOSFRANGO — Makefile (O Guia do Engenheiro)
# ============================================================

.PHONY: help setup up down logs shell-api seed migrate build clean install-hooks

# Comando padrão quando você digita apenas 'make'
help:
	@echo "🐔 MENOSFRANGO — Comandos disponíveis:"
	@echo "  make setup          → Configuração COMPLETA (Docker + Hooks + Env)"
	@echo "  make up             → Sobe o sistema em segundo plano"
	@echo "  make down           → Desliga os containers"
	@echo "  make logs           → Ver logs em tempo real (API + Front)"
	@echo "  make build          → Força a reconstrução das imagens"
	@echo "  make clean          → RESETA TUDO (apaga banco e volumes)"
	@echo "  make install-hooks  → Reinstala os filtros de segurança do Git"

setup:
	@echo "🚀 Iniciando configuração completa do MENOSFRANGO..."
	@# O comando 'cp -n' não sobrescreve se o arquivo já existir
	cp -n .env.example .env || echo "⚠️ .env já detectado."
	@# Instalando ferramentas de qualidade de código
	pip install pre-commit
	python -m pre_commit install
	@# Subindo a infraestrutura
	docker compose up -d --build
	@echo "✅ Setup concluído! Use 'make logs' para acompanhar a subida."

up:
	docker compose up -d

down:
	docker compose down

clean:
	@echo "🧨 BOTÃO DE PÂNICO: Apagando tudo..."
	docker compose down -v
	docker system prune -f
	@echo "✨ Tudo limpo. Use 'make setup' para recomeçar do zero."

logs:
	docker compose logs -f api frontend

shell-api:
	docker compose exec api bash

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python scripts/seed.py

build:
	docker compose build

install-hooks:
	pip install pre-commit
	python -m pre_commit install
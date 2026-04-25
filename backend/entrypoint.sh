#!/bin/sh

python backend/scripts/check_env.py

# Espera o banco de dados ficar pronto para não dar erro de conexão
echo "Aguardando o banco de dados..."
sleep 2

# 1. Executa as migrações (Cria as tabelas se não existirem)
echo "Executando migrações do Alembic..."
alembic upgrade head

# 2. Executa o Seed (Popula os dados se o banco estiver vazio)
echo "Populando banco de dados..."
python scripts/seed.py || echo "Seed já executado ou falhou, pulando..."

# 3. Inicia o servidor principal
echo "Iniciando FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
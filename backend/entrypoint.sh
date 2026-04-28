#!/bin/sh
set -e

echo "⏳ Aguardando o banco de dados aceitar conexões..."
until python -c "
import os
import sys
import psycopg

try:
    url = os.environ['DATABASE_URL'].replace('postgresql+psycopg', 'postgresql')
    conn = psycopg.connect(url)
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    echo "   Banco ainda não está pronto... aguardando 2s"
    sleep 2
done

echo "✅ Banco de dados pronto!"

echo "🔄 Executando migrações do Alembic..."
alembic upgrade head
echo "✅ Migrações aplicadas!"

echo "🌱 Populando banco de dados com dados demo..."
python scripts/seed.py || echo "ℹ️ Seed já executado ou pulado."

echo "🚀 Iniciando FastAPI na porta 8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

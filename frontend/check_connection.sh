#!/bin/sh

# ← CORRIGIDO: dentro do Docker, a API é acessada pelo nome do serviço "api", NÃO "localhost"
echo "🔍 Verificando conexão com a API..."

RETRIES=30
COUNT=0
until wget -q --spider http://api:8000/health 2>/dev/null; do
  COUNT=$((COUNT + 1))
  if [ $COUNT -ge $RETRIES ]; then
    echo "⚠️  API não respondeu em tempo. Iniciando frontend mesmo assim..."
    break
  fi
  echo "⏳ Aguardando API... ($COUNT/$RETRIES)"
  sleep 2
done

echo "✅ Verificação da API concluída."

# A automação para você nunca mais precisar rodar npm install no Windows:
echo "📦 Sincronizando dependências do Node..."
npm install

echo "🚀 Iniciando frontend..."
exec npm run dev
#!/bin/sh

echo "🔍 Iniciando teste de vizinhança..."

# Teste 1: A API está acessível?
echo "📡 Testando conexão com a API (Porta 8000)..."
if curl -s http://api:8000/health > /dev/null; then
    echo "✅ API encontrada e respondendo!"
else
    echo "❌ ERRO: Frontend não consegue falar com a API."
    echo "💡 Verifique se o container 'menosfrango_api' está rodando."
    exit 1
fi

echo "🚀 Tudo certo! O sistema está integrado. Iniciando Front-end..."
npm run dev
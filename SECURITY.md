# 🔒 Política de Segurança — Athletic AI

## Reportando Vulnerabilidades
Envie um e-mail para **security@athletic.ai** com descrição detalhada.
Resposta em até 72 horas.

## Práticas de Segurança
- **NUNCA** commite o arquivo `.env`
- Gere `JWT_SECRET` forte: `openssl rand -hex 32`
- Senhas: bcrypt com custo 12
- Tokens JWT: access 15min + refresh 7 dias
- CORS restrito às origens permitidas
- Rate limiting: 60 req/min/IP

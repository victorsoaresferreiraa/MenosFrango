# 🤝 Contribuindo com o Athletic AI

## Setup
```bash
git clone https://github.com/victorsoaresferreiraa/Athletic_Ai.git
cd Athletic_Ai
cp .env.example .env
docker compose up -d
```

## Fluxo
1. Fork → branch `feat/nome-feature`
2. Implemente seguindo os padrões do projeto
3. Teste com `docker compose exec api pytest tests/ -v`
4. Pull Request para `develop`

## Padrão de commits
```
feat: nova funcionalidade
fix: correção de bug
docs: documentação
refactor: refatoração
test: testes
```

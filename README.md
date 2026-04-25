# 🐔🤖 MENOSFRANGO

**A plataforma brasileira de treino inteligente para personais e alunos.**

> "Chega de ser frango. Treina com IA." 💪

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://docker.com)

---

## ✨ O que é o MENOSFRANGO?

Um SaaS completo que conecta **personal trainers** e **alunos**, com IA gerando planos de treino e nutrição personalizados.

### Para Alunos 🏃
- 🏋️ Registro de treinos com histórico completo
- 🥗 Controle nutricional com metas de macros
- 📸 Galeria de fotos de progresso
- 📊 Dashboard com gráficos de evolução
- 🤖 Planos gerados por IA (treino + nutrição + análise)
- 👨‍🏫 Acompanhamento pelo seu personal

### Para Personal Trainers 👨‍🏫
- 👥 Gestão completa de alunos
- 📩 Convite de alunos por e-mail
- 📊 Ver treinos e nutrição dos alunos
- 🤖 Gerar planos via IA para cada aluno
- 📝 Anotações privadas por aluno

---

## 🚀 Rodando em 3 comandos

```bash
git clone https://github.com/victorsoaresferreiraa/Athletic_Ai.git menosfrango
cd menosfrango
cp .env.example .env
docker compose up -d
```

Pronto! Acesse:
- 🌐 **Site:** http://localhost:3000
- 📖 **API Docs:** http://localhost:8000/docs

### Usuários demo

| Tipo | E-mail | Senha |
|------|--------|-------|
| 🏃 Aluno | demo@menosfrango.ai | 12345678 |
| 👨‍🏫 Personal | personal@menosfrango.ai | 12345678 |
| 👑 Admin | admin@menosfrango.ai | admin12345 |

---

## 🛠️ Stack

| Camada | Tecnologia |
|--------|-----------|
| Front-end | Next.js 14, TypeScript, Tailwind CSS |
| Back-end | Python, FastAPI, SQLAlchemy async |
| Banco | PostgreSQL 15 |
| Cache/Fila | Redis 7 + Celery |
| Storage | MinIO (S3-compatible) |
| IA | Modo A (offline) / Ollama / OpenAI / Anthropic |
| Infra | Docker Compose — 6 serviços |

---

## 🤖 Modos de IA

| Modo | Como funciona | Custo |
|------|--------------|-------|
| A | Fórmulas científicas (Mifflin-St Jeor, progressão linear) | Grátis |
| B | Ollama rodando local (Llama 3) | Grátis |
| C | OpenAI GPT-4 ou Anthropic Claude | Pago por uso |

Configure no `.env`: `FEATURE_FLAG_IA_MODE=A`

---

## 📁 Estrutura

```
menosfrango/
├── backend/
│   ├── app/
│   │   ├── api/v1/routers/     # Endpoints REST
│   │   ├── models/             # Tabelas do banco
│   │   ├── schemas/            # Validação Pydantic
│   │   ├── repositories/       # Queries
│   │   ├── services/           # IA, PDF, Storage
│   │   └── tasks/              # Celery tasks
│   ├── alembic/                # Migrações
│   └── tests/
├── frontend/
│   ├── public/
│   │   ├── mascote.svg         # 🐔🤖 O franguinho!
│   │   └── logo.svg
│   └── src/
│       ├── pages/
│       ├── components/layout/
│       └── lib/api.ts
├── docker-compose.yml
└── .env.example
```

---

## 📄 Licença

MIT © Victor Soares Ferreira  
UNISA — Engenharia de Software — Projeto Integrador 2025

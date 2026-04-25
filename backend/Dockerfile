# ESTÁGIO 1: O Construtor (Cozinha)
FROM python:3.11-slim as builder
WORKDIR /app
# Instala compiladores necessários para algumas bibliotecas de banco
RUN apt-get update && apt-get install -y gcc libpq-dev
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ESTÁGIO 2: O Executor (Mesa do Cliente)
FROM python:3.11-slim
WORKDIR /app
# Copia apenas as bibliotecas instaladas, sem o lixo dos compiladores
COPY --from=builder /root/.local /root/.local
COPY . .
# Ajusta o caminho para o Python achar as libs
ENV PATH=/root/.local/bin:$PATH
# Torna o script executável
RUN chmod +x entrypoint.sh scripts/*.py
CMD ["sh", "entrypoint.sh"]
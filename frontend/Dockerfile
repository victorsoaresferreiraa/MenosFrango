FROM node:20-alpine

WORKDIR /app

# 🛠️ A MÁGICA ACONTECE AQUI: 
# Instalamos o curl (o nosso "telefone") na versão Alpine do Linux
RUN apk add --no-cache curl

COPY package.json ./
RUN npm install
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
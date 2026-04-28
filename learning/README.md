🚀 Cheat Sheet: Sobrevivência Full Stack & DevOps
Este guia contém os comandos, conceitos e resoluções de problemas (troubleshooting) do nosso ambiente Docker, Next.js e CI/CD.

🛠️ 1. Comandos de Ouro (O Teu Cinto de Utilidades)
Docker (A Infraestrutura)
Ligar tudo em segundo plano: docker compose up -d (ou make up)

Desligar tudo: docker compose down

Ver quem está vivo (Status): docker compose ps

Ler a "Caixa Negra" (Logs em tempo real): docker compose logs -f <nome_do_servico> (ex: frontend, api, db)

Reconstruir um contentor (após mudar o Dockerfile): docker compose build <nome_do_servico>

Playwright (Testes E2E)
Entrar na pasta correta primeiro: cd frontend

Instalar as dependências e navegadores: npm install seguido de npx playwright install

Acordar o "Cliente Fantasma" (Testar): npx playwright test

🧠 2. Glossário do Engenheiro (Para não esquecer)
Liveness vs Readiness: * Liveness: O servidor está ligado? (O coração bate?)

Readiness: O servidor está pronto a receber tráfego? (O cérebro já acordou?) Usamos o nosso script check_connection.sh para testar a Readiness.

Working Directory (Contexto): Onde estás a executar o comando importa. Tentar correr o Playwright na raiz do projeto (onde não há o package.json do frontend) vai gerar o erro MODULE_NOT_FOUND.

CI/CD (GitHub Actions): É o nosso "Inspetor de Qualidade Automático". O ficheiro test.yml garante que o robô testa o código numa máquina virgem na nuvem antes de o aceitar.

Imagens Alpine (-alpine): São versões do Linux minúsculas e "carecas". Não trazem ferramentas como o curl instaladas de fábrica para poupar memória.

🕵️ 3. Troubleshooting (Os Erros Clássicos)
❌ Erro: /app/check_connection.sh: curl: not found
O que é: O contentor do frontend (usando Alpine Linux) não tem a ferramenta de rede curl para testar se a API está viva.

A Solução: Adicionar a instalação no Dockerfile do frontend:

Dockerfile
RUN apk add --no-cache curl
❌ Erro: Cannot find module '@playwright/test'
O que é: O Node.js não encontrou a biblioteca porque (1) estás na pasta errada ou (2) não a compraste (instalaste).

A Solução: 1. Vai para a pasta do frontend: cd frontend
2. Instala a ferramenta como dependência de desenvolvimento: npm install -D @playwright/test

❌ Erro: Ecrã Branco no localhost:3000 / ERR_CONNECTION_RESET (Next.js no Windows)
O que é: Corrupção de cache entre o Windows e o Linux do Docker enquanto o Next.js tenta compilar os ficheiros (chunks) Javascript.

A Solução (Limpeza de Cache):

Pára o contentor: docker compose stop frontend

Pelo Windows/VS Code, apaga a pasta .next dentro da pasta frontend.

Volta a ligar: docker compose start frontend

Aguarda a mensagem Compiled successfully nos logs antes de abrir no navegador.
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // A pasta onde seus testes vão morar (se você usou e2e, mude aqui)
  testDir: './e2e',
  
  // Rodar testes em paralelo para ser mais rápido
  fullyParallel: true,
  
  // Retentar testes que falharam se estiver no GitHub Actions (CI)
  retries: process.env.CI ? 2 : 0,
  
  // Quantidade de robôs trabalhando ao mesmo tempo
  workers: process.env.CI ? 1 : undefined,
  
  // Como ele vai te mostrar o resultado
  reporter: 'html',

  use: {
    // O pulo do gato: A URL base para ele não se perder
    baseURL: 'http://localhost:3000',

    // Coleta um "raio-x" se o teste falhar para te ajudar a debugar
    trace: 'on-first-retry',
  },

  // Vamos testar apenas no Chrome por enquanto para ser rápido
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
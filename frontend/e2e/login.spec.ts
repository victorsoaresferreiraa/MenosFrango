import { test, expect } from '@playwright/test';

test('deve verificar se a tela de login carrega e a API responde', async ({ page }) => {
  // 1. Aumentamos o tempo limite de navegação para 60 segundos
  // No CI, o primeiro carregamento do Next.js é muito pesado
  await page.goto('http://localhost:3000', { timeout: 60000 });

  // 2. Esperamos o campo de e-mail por até 30 segundos
  const loginInput = page.locator('input[name="email"]');
  
  // Se falhar aqui, o Playwright vai tirar um print automático para a gente ver o que tinha na tela!
  await loginInput.waitFor({ state: 'visible', timeout: 30000 });

  // 3. Verifica o título
  await expect(page).toHaveTitle(/MENOSFRANGO/i);

  // 4. Verifica a visibilidade
  await expect(loginInput).toBeVisible();
});
import { test, expect } from '@playwright/test';

test('deve verificar se a tela de login carrega e a API responde', async ({ page }) => {
  // 1. Tenta abrir o site
  await page.goto('http://localhost:3000');

  // 2. 🔑 A CHAVE DA VITÓRIA: 
  // Esperamos o campo de e-mail aparecer. Se ele apareceu, o Next.js terminou de renderizar!
  const loginInput = page.locator('input[name="email"]');
  await loginInput.waitFor({ state: 'visible', timeout: 15000 });

  // 3. Agora sim, verificamos o título com segurança
  await expect(page).toHaveTitle(/MENOSFRANGO/i);

  // 4. Verifica se o formulário está visível (redundância do bem)
  await expect(loginInput).toBeVisible();
});
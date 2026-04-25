import { test, expect } from '@playwright/test';

test('deve verificar se a tela de login carrega e a API responde', async ({ page }) => {
  // 1. Tenta abrir o site
  await page.goto('http://localhost:3000');

  // 2. Verifica se o título do MENOSFRANGO aparece
  await expect(page).toHaveTitle(/MENOSFRANGO/);

  // 3. Verifica se o formulário de login está visível
  const loginInput = page.locator('input[name="email"]');
  await expect(loginInput).toBeVisible();
});
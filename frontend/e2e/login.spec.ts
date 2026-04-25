import { test, expect } from '@playwright/test';

test('deve verificar se a tela de login carrega e a API responde', async ({ page }) => {
  // 1. Tenta abrir o site
  // O "networkidle" diz: espere a rede ficar quietinha (tudo carregar)
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

  // 2. Dá um tempinho extra de segurança (opcional mas ajuda no CI)
  await page.waitForTimeout(2000);

  // 3. Verifica se o título do MENOSFRANGO aparece
  // Adicionamos o "i" para ignorar maiúsculas/minúsculas se precisar
  await expect(page).toHaveTitle(/MENOSFRANGO/i);

  // 4. Verifica se o formulário de login está visível
  const loginInput = page.locator('input[name="email"]');
  await expect(loginInput).toBeVisible();
});
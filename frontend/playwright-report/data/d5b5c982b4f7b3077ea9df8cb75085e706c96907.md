# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: login.spec.ts >> deve verificar se a tela de login carrega e a API responde
- Location: e2e\login.spec.ts:3:5

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.goto: net::ERR_CONNECTION_RESET at http://localhost:3000/
Call log:
  - navigating to "http://localhost:3000/", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('deve verificar se a tela de login carrega e a API responde', async ({ page }) => {
  4  |   // 1. Tenta abrir o site
> 5  |   await page.goto('http://localhost:3000');
     |              ^ Error: page.goto: net::ERR_CONNECTION_RESET at http://localhost:3000/
  6  | 
  7  |   // 2. Verifica se o título do MENOSFRANGO aparece
  8  |   await expect(page).toHaveTitle(/MENOSFRANGO/);
  9  | 
  10 |   // 3. Verifica se o formulário de login está visível
  11 |   const loginInput = page.locator('input[name="email"]');
  12 |   await expect(loginInput).toBeVisible();
  13 | });
```
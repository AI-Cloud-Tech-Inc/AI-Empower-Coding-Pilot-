import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page, request }) => {
    // Create test user via API and log in
    const user = `dash_test_${Date.now()}`;
    await request.post('http://localhost:8000/api/auth/signup', {
      data: { username: user, email: `${user}@test.com`, password: 'TestPass123' },
    });
    const loginRes = await request.post('http://localhost:8000/api/auth/login', {
      data: { username: user, password: 'TestPass123' },
    });
    const { access_token, user: userData } = await loginRes.json();

    // Set auth in localStorage and navigate
    await page.goto('/');
    await page.evaluate(
      ([token, u]) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(u));
      },
      [access_token, userData],
    );
    await page.goto('/');
    await expect(page.locator('h2')).toContainText('Dashboard', { timeout: 5000 });
  });

  test('displays status cards', async ({ page }) => {
    await expect(page.locator('text=Status')).toBeVisible();
    await expect(page.locator('text=Version')).toBeVisible();
    await expect(page.locator('text=Services')).toBeVisible();
  });

  test('displays feature badges', async ({ page }) => {
    await expect(page.locator('text=Platform Capabilities')).toBeVisible();
    await expect(page.locator('text=Multi-Agent Orchestration')).toBeVisible();
  });

  test('can run pipeline', async ({ page }) => {
    await page.fill('textarea', 'Build a simple REST API');
    await page.click('text=Run Pipeline');
    await expect(page.locator('text=Pipeline Result')).toBeVisible({ timeout: 15000 });
  });

  test('sidebar navigation works', async ({ page }) => {
    await page.click('text=Agents (9)');
    await expect(page.locator('h2')).toContainText('Agent Status');

    await page.click('text=Compliance');
    await expect(page.locator('h2')).toContainText('Compliance');

    await page.click('text=Dashboard');
    await expect(page.locator('h2')).toContainText('Dashboard');
  });
});

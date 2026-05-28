import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('shows login page by default', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('AI-Empower');
    await expect(page.locator('h2')).toContainText('Sign In');
  });

  test('can toggle between login and signup', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h2')).toContainText('Sign In');
    await page.click('text=Sign Up');
    await expect(page.locator('h2')).toContainText('Create Account');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await page.click('text=Sign In');
    await expect(page.locator('h2')).toContainText('Sign In');
  });

  test('shows error on invalid login', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[placeholder="Enter username"]', 'nobody');
    await page.fill('input[placeholder="Enter password"]', 'wrongpass');
    await page.click('button[type="submit"]');
    await expect(page.locator('.bg-red-500\\/20')).toBeVisible({ timeout: 5000 });
  });

  test('signup and login flow', async ({ page }) => {
    const user = `pw_test_${Date.now()}`;
    await page.goto('/');

    // Signup
    await page.click('text=Sign Up');
    await page.fill('input[placeholder="Enter username"]', user);
    await page.fill('input[placeholder="Enter email"]', `${user}@test.com`);
    await page.fill('input[placeholder="Enter password"]', 'TestPassword123');
    await page.click('button[type="submit"]');

    // Should land on dashboard
    await expect(page.locator('h2')).toContainText('Dashboard', { timeout: 5000 });
  });
});

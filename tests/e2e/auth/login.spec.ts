import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers';

test.describe('Authentication - Login', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    await page.goto('/login');
  });

  test('should display login form correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/DealVerse OS/);
    
    // Check form elements
    await expect(page.locator('[data-testid="email-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="forgot-password-link"]')).toBeVisible();
    
    // Check branding
    await expect(page.locator('[data-testid="logo"]')).toBeVisible();
    await expect(page.locator('text=DealVerse OS')).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    await helpers.login('test@dealverse.com', 'password123');
    
    // Verify successful login
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    await expect(page.locator('[data-testid="dashboard-header"]')).toContainText('Welcome');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('[data-testid="email-input"]', 'invalid@email.com');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    await page.click('[data-testid="login-button"]');
    
    // Check error message
    await helpers.waitForToast('Invalid credentials');
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    
    // Should stay on login page
    await expect(page).toHaveURL('/login');
  });

  test('should validate email format', async ({ page }) => {
    await page.fill('[data-testid="email-input"]', 'invalid-email');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Check validation error
    await expect(page.locator('[data-testid="email-error"]')).toContainText('Invalid email format');
  });

  test('should require password', async ({ page }) => {
    await page.fill('[data-testid="email-input"]', 'test@dealverse.com');
    await page.click('[data-testid="login-button"]');
    
    // Check validation error
    await expect(page.locator('[data-testid="password-error"]')).toContainText('Password is required');
  });

  test('should handle forgot password flow', async ({ page }) => {
    await page.click('[data-testid="forgot-password-link"]');
    
    // Should navigate to forgot password page
    await expect(page).toHaveURL('/forgot-password');
    await expect(page.locator('[data-testid="reset-email-input"]')).toBeVisible();
  });

  test('should show loading state during login', async ({ page }) => {
    // Simulate slow network
    await helpers.simulateSlowNetwork();
    
    await page.fill('[data-testid="email-input"]', 'test@dealverse.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Check loading state
    await expect(page.locator('[data-testid="login-button"]')).toBeDisabled();
    await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();
  });

  test('should redirect authenticated users', async ({ page }) => {
    // Login first
    await helpers.login();
    
    // Try to access login page
    await page.goto('/login');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
  });

  test('should work with keyboard navigation', async ({ page }) => {
    await helpers.testKeyboardNavigation('[data-testid="email-input"]', [
      '[data-testid="email-input"]',
      '[data-testid="password-input"]',
      '[data-testid="login-button"]',
      '[data-testid="forgot-password-link"]'
    ]);
  });

  test('should be responsive on mobile', async ({ page }) => {
    await helpers.testResponsiveDesign([
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 }
    ]);
    
    // Check mobile-specific elements
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('[data-testid="mobile-logo"]')).toBeVisible();
  });

  test('should handle session timeout', async ({ page }) => {
    await helpers.login();
    
    // Simulate session expiry
    await page.evaluate(() => {
      localStorage.removeItem('auth-token');
    });
    
    // Try to access protected route
    await page.goto('/dashboard/analytics');
    
    // Should redirect to login
    await expect(page).toHaveURL('/login');
    await helpers.waitForToast('Session expired. Please login again.');
  });

  test('should remember login preference', async ({ page }) => {
    await page.fill('[data-testid="email-input"]', 'test@dealverse.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.check('[data-testid="remember-me"]');
    await page.click('[data-testid="login-button"]');
    
    await page.waitForURL('/dashboard');
    
    // Check if remember me is stored
    const rememberMe = await page.evaluate(() => localStorage.getItem('remember-me'));
    expect(rememberMe).toBe('true');
  });
});

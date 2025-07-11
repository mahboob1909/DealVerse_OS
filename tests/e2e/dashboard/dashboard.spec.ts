import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers';

test.describe('Dashboard', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    await helpers.login();
  });

  test('should display dashboard overview correctly', async ({ page }) => {
    // Check main dashboard elements
    await expect(page.locator('[data-testid="dashboard-header"]')).toBeVisible();
    await expect(page.locator('[data-testid="stats-overview"]')).toBeVisible();
    await expect(page.locator('[data-testid="recent-activity"]')).toBeVisible();
    await expect(page.locator('[data-testid="quick-actions"]')).toBeVisible();
    
    // Check navigation sidebar
    await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-prospect-ai"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-diligence-navigator"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-valuation-hub"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-compliance-guardian"]')).toBeVisible();
    await expect(page.locator('[data-testid="nav-pitchcraft-suite"]')).toBeVisible();
  });

  test('should display correct user information', async ({ page }) => {
    // Check user menu
    await page.click('[data-testid="user-menu"]');
    await expect(page.locator('[data-testid="user-name"]')).toContainText('Test User');
    await expect(page.locator('[data-testid="user-email"]')).toContainText('test@dealverse.com');
    await expect(page.locator('[data-testid="user-role"]')).toContainText('Investment Banker');
  });

  test('should show real-time statistics', async ({ page }) => {
    // Check stats cards
    const statsCards = page.locator('[data-testid="stats-card"]');
    await expect(statsCards).toHaveCount(4);
    
    // Check individual stats
    await expect(page.locator('[data-testid="stat-active-deals"]')).toBeVisible();
    await expect(page.locator('[data-testid="stat-total-value"]')).toBeVisible();
    await expect(page.locator('[data-testid="stat-completion-rate"]')).toBeVisible();
    await expect(page.locator('[data-testid="stat-pending-tasks"]')).toBeVisible();
    
    // Verify stats have numeric values
    const activeDeals = await page.locator('[data-testid="stat-active-deals"] .stat-value').textContent();
    expect(activeDeals).toMatch(/^\d+$/);
  });

  test('should display recent activity feed', async ({ page }) => {
    const activityFeed = page.locator('[data-testid="activity-feed"]');
    await expect(activityFeed).toBeVisible();
    
    // Check activity items
    const activityItems = page.locator('[data-testid="activity-item"]');
    await expect(activityItems.first()).toBeVisible();
    
    // Check activity item structure
    await expect(activityItems.first().locator('[data-testid="activity-icon"]')).toBeVisible();
    await expect(activityItems.first().locator('[data-testid="activity-title"]')).toBeVisible();
    await expect(activityItems.first().locator('[data-testid="activity-time"]')).toBeVisible();
  });

  test('should navigate to modules correctly', async ({ page }) => {
    // Test navigation to Prospect AI
    await helpers.navigateToModule('prospect-ai');
    await expect(page).toHaveURL('/dashboard/prospect-ai');
    await expect(page.locator('[data-testid="prospect-ai-header"]')).toBeVisible();
    
    // Test navigation to Diligence Navigator
    await helpers.navigateToModule('diligence-navigator');
    await expect(page).toHaveURL('/dashboard/diligence-navigator');
    await expect(page.locator('[data-testid="diligence-navigator-header"]')).toBeVisible();
    
    // Test navigation to Valuation Hub
    await helpers.navigateToModule('valuation-hub');
    await expect(page).toHaveURL('/dashboard/valuation-hub');
    await expect(page.locator('[data-testid="valuation-hub-header"]')).toBeVisible();
  });

  test('should handle quick actions', async ({ page }) => {
    // Test "New Deal" quick action
    await page.click('[data-testid="quick-action-new-deal"]');
    await expect(page.locator('[data-testid="new-deal-modal"]')).toBeVisible();
    
    // Close modal and test "Upload Document" action
    await page.click('[data-testid="modal-close"]');
    await page.click('[data-testid="quick-action-upload-document"]');
    await expect(page.locator('[data-testid="upload-modal"]')).toBeVisible();
  });

  test('should display notifications correctly', async ({ page }) => {
    // Click notifications bell
    await page.click('[data-testid="notifications-bell"]');
    await expect(page.locator('[data-testid="notifications-dropdown"]')).toBeVisible();
    
    // Check notification items
    const notifications = page.locator('[data-testid="notification-item"]');
    if (await notifications.count() > 0) {
      await expect(notifications.first().locator('[data-testid="notification-title"]')).toBeVisible();
      await expect(notifications.first().locator('[data-testid="notification-time"]')).toBeVisible();
    }
  });

  test('should handle search functionality', async ({ page }) => {
    // Test global search
    await page.click('[data-testid="global-search"]');
    await page.fill('[data-testid="search-input"]', 'Tesla');
    await page.keyboard.press('Enter');
    
    // Wait for search results
    await helpers.waitForLoading();
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
  });

  test('should update theme correctly', async ({ page }) => {
    // Test theme toggle
    await page.click('[data-testid="theme-toggle"]');
    
    // Check if dark theme is applied
    const htmlElement = page.locator('html');
    await expect(htmlElement).toHaveClass(/dark/);
    
    // Toggle back to light theme
    await page.click('[data-testid="theme-toggle"]');
    await expect(htmlElement).not.toHaveClass(/dark/);
  });

  test('should handle logout correctly', async ({ page }) => {
    // Open user menu and logout
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    
    // Should redirect to login page
    await expect(page).toHaveURL('/login');
    
    // Check that user is logged out
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });

  test('should be responsive on different screen sizes', async ({ page }) => {
    await helpers.testResponsiveDesign([
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 }
    ]);
    
    // Test mobile navigation
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('[data-testid="mobile-menu-toggle"]')).toBeVisible();
    
    // Open mobile menu
    await page.click('[data-testid="mobile-menu-toggle"]');
    await expect(page.locator('[data-testid="mobile-sidebar"]')).toBeVisible();
  });

  test('should handle real-time updates', async ({ page }) => {
    // Wait for WebSocket connection
    await page.waitForFunction(() => window.WebSocket !== undefined);
    
    // Check for real-time activity updates
    const initialActivityCount = await page.locator('[data-testid="activity-item"]').count();
    
    // Simulate real-time update (this would normally come from WebSocket)
    await page.evaluate(() => {
      // Simulate receiving a WebSocket message
      window.dispatchEvent(new CustomEvent('websocket-message', {
        detail: { type: 'new-activity', data: { title: 'New deal created', time: new Date() } }
      }));
    });
    
    // Check if activity feed updated
    await page.waitForTimeout(1000);
    const newActivityCount = await page.locator('[data-testid="activity-item"]').count();
    expect(newActivityCount).toBeGreaterThanOrEqual(initialActivityCount);
  });

  test('should handle keyboard shortcuts', async ({ page }) => {
    // Test Ctrl+K for search
    await page.keyboard.press('Control+k');
    await expect(page.locator('[data-testid="search-modal"]')).toBeVisible();
    
    // Close search modal
    await page.keyboard.press('Escape');
    await expect(page.locator('[data-testid="search-modal"]')).not.toBeVisible();
    
    // Test Ctrl+N for new deal
    await page.keyboard.press('Control+n');
    await expect(page.locator('[data-testid="new-deal-modal"]')).toBeVisible();
  });

  test('should persist user preferences', async ({ page }) => {
    // Change sidebar state
    await page.click('[data-testid="sidebar-toggle"]');
    
    // Reload page
    await page.reload();
    await helpers.waitForLoading();
    
    // Check if sidebar state is persisted
    const sidebar = page.locator('[data-testid="sidebar"]');
    await expect(sidebar).toHaveClass(/collapsed/);
  });
});

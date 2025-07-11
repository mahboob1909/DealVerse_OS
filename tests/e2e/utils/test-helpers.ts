import { Page, expect } from '@playwright/test';

export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * Login with test credentials
   */
  async login(email: string = 'test@dealverse.com', password: string = 'password123') {
    await this.page.goto('/login');
    await this.page.fill('[data-testid="email-input"]', email);
    await this.page.fill('[data-testid="password-input"]', password);
    await this.page.click('[data-testid="login-button"]');
    
    // Wait for successful login redirect
    await this.page.waitForURL('/dashboard');
    await expect(this.page.locator('[data-testid="dashboard-header"]')).toBeVisible();
  }

  /**
   * Navigate to a specific module
   */
  async navigateToModule(moduleName: string) {
    await this.page.click(`[data-testid="nav-${moduleName.toLowerCase()}"]`);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Wait for API response
   */
  async waitForApiResponse(urlPattern: string | RegExp, timeout: number = 10000) {
    return await this.page.waitForResponse(
      response => {
        const url = response.url();
        if (typeof urlPattern === 'string') {
          return url.includes(urlPattern);
        }
        return urlPattern.test(url);
      },
      { timeout }
    );
  }

  /**
   * Upload a test file
   */
  async uploadFile(inputSelector: string, filePath: string) {
    const fileInput = this.page.locator(inputSelector);
    await fileInput.setInputFiles(filePath);
  }

  /**
   * Wait for loading to complete
   */
  async waitForLoading() {
    await this.page.waitForSelector('[data-testid="loading-spinner"]', { state: 'hidden' });
  }

  /**
   * Take screenshot with timestamp
   */
  async takeScreenshot(name: string) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await this.page.screenshot({ 
      path: `test-results/screenshots/${name}-${timestamp}.png`,
      fullPage: true 
    });
  }

  /**
   * Check if element is visible and enabled
   */
  async isElementReady(selector: string) {
    const element = this.page.locator(selector);
    await expect(element).toBeVisible();
    await expect(element).toBeEnabled();
    return element;
  }

  /**
   * Fill form with data
   */
  async fillForm(formData: Record<string, string>) {
    for (const [field, value] of Object.entries(formData)) {
      await this.page.fill(`[data-testid="${field}"]`, value);
    }
  }

  /**
   * Wait for toast notification
   */
  async waitForToast(message?: string) {
    const toast = this.page.locator('[data-testid="toast"]');
    await expect(toast).toBeVisible();
    
    if (message) {
      await expect(toast).toContainText(message);
    }
    
    return toast;
  }

  /**
   * Check table data
   */
  async verifyTableData(tableSelector: string, expectedData: string[][]) {
    const table = this.page.locator(tableSelector);
    await expect(table).toBeVisible();
    
    for (let i = 0; i < expectedData.length; i++) {
      const row = table.locator(`tbody tr:nth-child(${i + 1})`);
      for (let j = 0; j < expectedData[i].length; j++) {
        const cell = row.locator(`td:nth-child(${j + 1})`);
        await expect(cell).toContainText(expectedData[i][j]);
      }
    }
  }

  /**
   * Simulate real user typing
   */
  async typeSlowly(selector: string, text: string, delay: number = 100) {
    const element = this.page.locator(selector);
    await element.click();
    await element.clear();
    
    for (const char of text) {
      await element.type(char);
      await this.page.waitForTimeout(delay);
    }
  }

  /**
   * Check responsive design
   */
  async testResponsiveDesign(breakpoints: { name: string; width: number; height: number }[]) {
    for (const breakpoint of breakpoints) {
      await this.page.setViewportSize({ width: breakpoint.width, height: breakpoint.height });
      await this.page.waitForTimeout(500); // Allow layout to settle
      await this.takeScreenshot(`responsive-${breakpoint.name}`);
    }
  }

  /**
   * Test keyboard navigation
   */
  async testKeyboardNavigation(startSelector: string, expectedSelectors: string[]) {
    await this.page.click(startSelector);
    
    for (const selector of expectedSelectors) {
      await this.page.keyboard.press('Tab');
      await expect(this.page.locator(selector)).toBeFocused();
    }
  }

  /**
   * Simulate network conditions
   */
  async simulateSlowNetwork() {
    await this.page.route('**/*', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
      await route.continue();
    });
  }

  /**
   * Clear all data and reset state
   */
  async resetTestState() {
    await this.page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await this.page.reload();
  }
}

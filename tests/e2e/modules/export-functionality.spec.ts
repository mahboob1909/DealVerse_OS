import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers';

test.describe('Export Functionality', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    await helpers.login();
  });

  test('should export PDF reports from Diligence Navigator', async ({ page }) => {
    await helpers.navigateToModule('diligence-navigator');
    
    // Open export modal
    await page.click('[data-testid="export-report-btn"]');
    await expect(page.locator('[data-testid="export-modal"]')).toBeVisible();
    
    // Configure export options
    await page.selectOption('[data-testid="export-format"]', 'pdf');
    await page.check('[data-testid="include-executive-summary"]');
    await page.check('[data-testid="include-risk-assessment"]');
    await page.check('[data-testid="include-entity-extraction"]');
    await page.check('[data-testid="include-compliance-check"]');
    
    // Start export and wait for download
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-confirm-btn"]');
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/diligence-report-\d{4}-\d{2}-\d{2}\.pdf$/);
    
    // Verify export success notification
    await helpers.waitForToast('PDF report exported successfully');
  });

  test('should export Excel reports from Valuation Hub', async ({ page }) => {
    await helpers.navigateToModule('valuation-hub');
    
    // Create a valuation model first
    await page.click('[data-testid="new-valuation-btn"]');
    await helpers.fillForm({
      'company-name': 'Test Company',
      'valuation-method': 'dcf',
      'revenue': '1000000',
      'growth-rate': '15'
    });
    await page.click('[data-testid="create-valuation-btn"]');
    await helpers.waitForLoading();
    
    // Export valuation model
    await page.click('[data-testid="export-valuation-btn"]');
    await page.selectOption('[data-testid="export-format"]', 'excel');
    
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-confirm-btn"]');
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/valuation-model.*\.xlsx$/);
  });

  test('should export PowerPoint presentations from PitchCraft Suite', async ({ page }) => {
    await helpers.navigateToModule('pitchcraft-suite');
    
    // Create a pitch deck
    await page.click('[data-testid="new-pitch-btn"]');
    await page.fill('[data-testid="pitch-title"]', 'Investment Opportunity');
    await page.selectOption('[data-testid="template-select"]', 'investment-banking');
    await page.click('[data-testid="create-pitch-btn"]');
    await helpers.waitForLoading();
    
    // Add some content
    await page.click('[data-testid="add-slide-btn"]');
    await page.selectOption('[data-testid="slide-type"]', 'financial-overview');
    await page.click('[data-testid="add-slide-confirm"]');
    
    // Export presentation
    await page.click('[data-testid="export-presentation-btn"]');
    await page.selectOption('[data-testid="export-format"]', 'powerpoint');
    
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-confirm-btn"]');
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/pitch-deck.*\.pptx$/);
  });

  test('should export custom reports with advanced analytics', async ({ page }) => {
    await helpers.navigateToModule('advanced-analytics');
    
    // Create custom report
    await page.click('[data-testid="create-custom-report-btn"]');
    await page.fill('[data-testid="report-title"]', 'Q4 Investment Analysis');
    
    // Select data sources
    await page.check('[data-testid="data-source-deals"]');
    await page.check('[data-testid="data-source-valuations"]');
    await page.check('[data-testid="data-source-market-data"]');
    
    // Configure visualizations
    await page.click('[data-testid="add-chart-btn"]');
    await page.selectOption('[data-testid="chart-type"]', 'bar-chart');
    await page.selectOption('[data-testid="chart-data"]', 'deal-volume');
    await page.click('[data-testid="add-chart-confirm"]');
    
    // Generate report
    await page.click('[data-testid="generate-report-btn"]');
    await helpers.waitForApiResponse('/api/analytics/generate-report');
    await helpers.waitForLoading();
    
    // Export report
    await page.click('[data-testid="export-analytics-report-btn"]');
    await page.selectOption('[data-testid="export-format"]', 'pdf');
    await page.check('[data-testid="include-raw-data"]');
    
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-confirm-btn"]');
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/analytics-report.*\.pdf$/);
  });

  test('should handle bulk export operations', async ({ page }) => {
    await helpers.navigateToModule('diligence-navigator');
    
    // Select multiple documents
    await page.check('[data-testid="document-checkbox-1"]');
    await page.check('[data-testid="document-checkbox-2"]');
    await page.check('[data-testid="document-checkbox-3"]');
    
    // Open bulk export
    await page.click('[data-testid="bulk-export-btn"]');
    await expect(page.locator('[data-testid="bulk-export-modal"]')).toBeVisible();
    
    // Configure bulk export
    await page.selectOption('[data-testid="bulk-export-format"]', 'zip');
    await page.check('[data-testid="include-analysis-reports"]');
    await page.check('[data-testid="include-source-documents"]');
    
    // Start bulk export
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="start-bulk-export-btn"]');
    
    // Wait for export progress
    await expect(page.locator('[data-testid="export-progress"]')).toBeVisible();
    await helpers.waitForApiResponse('/api/export/bulk');
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/bulk-export.*\.zip$/);
  });

  test('should handle export with custom branding', async ({ page }) => {
    // Navigate to settings first
    await page.goto('/dashboard/settings');
    
    // Configure branding
    await page.click('[data-testid="branding-tab"]');
    await page.fill('[data-testid="company-name"]', 'Custom Investment Bank');
    await page.fill('[data-testid="company-logo-url"]', 'https://example.com/logo.png');
    await page.selectOption('[data-testid="brand-color"]', '#1a2332');
    await page.click('[data-testid="save-branding-btn"]');
    
    // Go back to module and export
    await helpers.navigateToModule('diligence-navigator');
    await page.click('[data-testid="export-report-btn"]');
    
    // Enable custom branding
    await page.check('[data-testid="use-custom-branding"]');
    await page.selectOption('[data-testid="export-format"]', 'pdf');
    
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-confirm-btn"]');
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/branded-report.*\.pdf$/);
  });

  test('should handle export scheduling', async ({ page }) => {
    await helpers.navigateToModule('advanced-analytics');
    
    // Create scheduled export
    await page.click('[data-testid="schedule-export-btn"]');
    await expect(page.locator('[data-testid="schedule-export-modal"]')).toBeVisible();
    
    // Configure schedule
    await page.fill('[data-testid="export-name"]', 'Weekly Deal Summary');
    await page.selectOption('[data-testid="export-frequency"]', 'weekly');
    await page.selectOption('[data-testid="export-day"]', 'monday');
    await page.fill('[data-testid="export-time"]', '09:00');
    await page.fill('[data-testid="export-email"]', 'reports@dealverse.com');
    
    // Save schedule
    await page.click('[data-testid="save-schedule-btn"]');
    await helpers.waitForToast('Export schedule created successfully');
    
    // Verify schedule appears in list
    await expect(page.locator('[data-testid="scheduled-export-item"]')).toBeVisible();
    await expect(page.locator('[data-testid="schedule-name"]')).toContainText('Weekly Deal Summary');
  });

  test('should handle export permissions and access control', async ({ page }) => {
    await helpers.navigateToModule('diligence-navigator');
    
    // Try to export sensitive document (should require additional permissions)
    await page.click('[data-testid="sensitive-document-export"]');
    await expect(page.locator('[data-testid="permission-required-modal"]')).toBeVisible();
    
    // Enter additional authentication
    await page.fill('[data-testid="permission-password"]', 'admin123');
    await page.click('[data-testid="confirm-permission-btn"]');
    
    // Now export should proceed
    await page.selectOption('[data-testid="export-format"]', 'pdf');
    await page.check('[data-testid="watermark-confidential"]');
    
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-confirm-btn"]');
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/confidential-report.*\.pdf$/);
  });

  test('should track export history and audit trail', async ({ page }) => {
    // Navigate to export history
    await page.goto('/dashboard/settings/export-history');
    
    // Check export history table
    await expect(page.locator('[data-testid="export-history-table"]')).toBeVisible();
    
    // Verify columns
    await expect(page.locator('[data-testid="column-export-name"]')).toBeVisible();
    await expect(page.locator('[data-testid="column-export-date"]')).toBeVisible();
    await expect(page.locator('[data-testid="column-export-user"]')).toBeVisible();
    await expect(page.locator('[data-testid="column-export-format"]')).toBeVisible();
    await expect(page.locator('[data-testid="column-export-status"]')).toBeVisible();
    
    // Test filtering
    await page.selectOption('[data-testid="filter-format"]', 'pdf');
    await page.click('[data-testid="apply-filter-btn"]');
    
    // Check filtered results
    const exportRows = page.locator('[data-testid="export-row"]');
    if (await exportRows.count() > 0) {
      await expect(exportRows.first().locator('[data-testid="export-format"]')).toContainText('PDF');
    }
  });

  test('should handle export errors gracefully', async ({ page }) => {
    await helpers.navigateToModule('diligence-navigator');
    
    // Simulate network error during export
    await page.route('**/api/export/**', route => route.abort());
    
    await page.click('[data-testid="export-report-btn"]');
    await page.selectOption('[data-testid="export-format"]', 'pdf');
    await page.click('[data-testid="export-confirm-btn"]');
    
    // Check error handling
    await helpers.waitForToast('Export failed. Please try again.');
    await expect(page.locator('[data-testid="export-error-message"]')).toBeVisible();
    
    // Test retry functionality
    await page.click('[data-testid="retry-export-btn"]');
    
    // Remove network error simulation
    await page.unroute('**/api/export/**');
    
    // Export should now succeed
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-confirm-btn"]');
    
    const download = await downloadPromise;
    expect(download).toBeTruthy();
  });
});

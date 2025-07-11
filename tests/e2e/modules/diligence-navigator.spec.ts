import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers';
import path from 'path';

test.describe('Diligence Navigator Module', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    await helpers.login();
    await helpers.navigateToModule('diligence-navigator');
  });

  test('should display module interface correctly', async ({ page }) => {
    // Check main components
    await expect(page.locator('[data-testid="diligence-navigator-header"]')).toBeVisible();
    await expect(page.locator('[data-testid="document-upload-area"]')).toBeVisible();
    await expect(page.locator('[data-testid="analysis-dashboard"]')).toBeVisible();
    await expect(page.locator('[data-testid="risk-assessment-panel"]')).toBeVisible();
    
    // Check action buttons
    await expect(page.locator('[data-testid="upload-document-btn"]')).toBeVisible();
    await expect(page.locator('[data-testid="start-analysis-btn"]')).toBeVisible();
    await expect(page.locator('[data-testid="export-report-btn"]')).toBeVisible();
  });

  test('should handle document upload successfully', async ({ page }) => {
    // Create a test file path (you would need actual test files)
    const testFilePath = path.join(__dirname, '../../fixtures/test-document.pdf');
    
    // Upload document
    await page.click('[data-testid="upload-document-btn"]');
    await expect(page.locator('[data-testid="upload-modal"]')).toBeVisible();
    
    // Simulate file upload
    await helpers.uploadFile('[data-testid="file-input"]', testFilePath);
    await page.click('[data-testid="upload-confirm-btn"]');
    
    // Wait for upload completion
    await helpers.waitForToast('Document uploaded successfully');
    await helpers.waitForLoading();
    
    // Verify document appears in list
    await expect(page.locator('[data-testid="document-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="document-item"]').first()).toBeVisible();
  });

  test('should perform AI document analysis', async ({ page }) => {
    // Assume document is already uploaded
    await page.click('[data-testid="start-analysis-btn"]');
    
    // Wait for analysis to start
    await expect(page.locator('[data-testid="analysis-progress"]')).toBeVisible();
    await helpers.waitForApiResponse('/api/ai/analyze-document');
    
    // Wait for analysis completion
    await helpers.waitForLoading();
    await helpers.waitForToast('Analysis completed');
    
    // Check analysis results
    await expect(page.locator('[data-testid="analysis-results"]')).toBeVisible();
    await expect(page.locator('[data-testid="key-findings"]')).toBeVisible();
    await expect(page.locator('[data-testid="risk-indicators"]')).toBeVisible();
    await expect(page.locator('[data-testid="compliance-check"]')).toBeVisible();
  });

  test('should display risk assessment correctly', async ({ page }) => {
    // Navigate to risk assessment tab
    await page.click('[data-testid="risk-assessment-tab"]');
    
    // Check risk categories
    await expect(page.locator('[data-testid="financial-risk"]')).toBeVisible();
    await expect(page.locator('[data-testid="operational-risk"]')).toBeVisible();
    await expect(page.locator('[data-testid="legal-risk"]')).toBeVisible();
    await expect(page.locator('[data-testid="market-risk"]')).toBeVisible();
    
    // Check risk scores
    const riskScores = page.locator('[data-testid="risk-score"]');
    await expect(riskScores).toHaveCount(4);
    
    // Verify risk score format (should be percentage or numeric)
    const firstRiskScore = await riskScores.first().textContent();
    expect(firstRiskScore).toMatch(/\d+(\.\d+)?%?/);
  });

  test('should handle entity extraction', async ({ page }) => {
    // Navigate to entity extraction tab
    await page.click('[data-testid="entity-extraction-tab"]');
    
    // Check extracted entities
    await expect(page.locator('[data-testid="entities-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="entity-companies"]')).toBeVisible();
    await expect(page.locator('[data-testid="entity-people"]')).toBeVisible();
    await expect(page.locator('[data-testid="entity-locations"]')).toBeVisible();
    await expect(page.locator('[data-testid="entity-dates"]')).toBeVisible();
    
    // Test entity filtering
    await page.click('[data-testid="filter-companies"]');
    const companyEntities = page.locator('[data-testid="entity-item"][data-type="company"]');
    await expect(companyEntities.first()).toBeVisible();
  });

  test('should generate compliance report', async ({ page }) => {
    // Navigate to compliance tab
    await page.click('[data-testid="compliance-tab"]');
    
    // Check compliance categories
    await expect(page.locator('[data-testid="regulatory-compliance"]')).toBeVisible();
    await expect(page.locator('[data-testid="data-privacy"]')).toBeVisible();
    await expect(page.locator('[data-testid="financial-regulations"]')).toBeVisible();
    
    // Generate compliance report
    await page.click('[data-testid="generate-compliance-report"]');
    await helpers.waitForApiResponse('/api/compliance/generate-report');
    
    // Check report generation
    await helpers.waitForToast('Compliance report generated');
    await expect(page.locator('[data-testid="compliance-report"]')).toBeVisible();
  });

  test('should export analysis results', async ({ page }) => {
    // Click export button
    await page.click('[data-testid="export-report-btn"]');
    await expect(page.locator('[data-testid="export-modal"]')).toBeVisible();
    
    // Select export format
    await page.selectOption('[data-testid="export-format"]', 'pdf');
    await page.check('[data-testid="include-risk-assessment"]');
    await page.check('[data-testid="include-entities"]');
    
    // Start export
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-confirm-btn"]');
    
    // Wait for download
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/diligence-report.*\.pdf$/);
  });

  test('should handle real-time collaboration', async ({ page }) => {
    // Add comment to analysis
    await page.click('[data-testid="add-comment-btn"]');
    await page.fill('[data-testid="comment-input"]', 'This requires further review');
    await page.click('[data-testid="submit-comment-btn"]');
    
    // Check comment appears
    await expect(page.locator('[data-testid="comment-item"]').last()).toContainText('This requires further review');
    
    // Test @mention functionality
    await page.click('[data-testid="add-comment-btn"]');
    await page.fill('[data-testid="comment-input"]', '@john.doe Please review this section');
    await page.click('[data-testid="submit-comment-btn"]');
    
    // Check mention notification
    await helpers.waitForToast('John Doe has been notified');
  });

  test('should handle document comparison', async ({ page }) => {
    // Navigate to comparison tab
    await page.click('[data-testid="comparison-tab"]');
    
    // Select documents to compare
    await page.selectOption('[data-testid="document-1-select"]', 'document-1');
    await page.selectOption('[data-testid="document-2-select"]', 'document-2');
    await page.click('[data-testid="start-comparison-btn"]');
    
    // Wait for comparison results
    await helpers.waitForApiResponse('/api/ai/compare-documents');
    await helpers.waitForLoading();
    
    // Check comparison results
    await expect(page.locator('[data-testid="comparison-results"]')).toBeVisible();
    await expect(page.locator('[data-testid="differences-highlighted"]')).toBeVisible();
    await expect(page.locator('[data-testid="similarity-score"]')).toBeVisible();
  });

  test('should handle search and filtering', async ({ page }) => {
    // Test document search
    await page.fill('[data-testid="document-search"]', 'financial');
    await page.keyboard.press('Enter');
    
    // Check filtered results
    await helpers.waitForLoading();
    const searchResults = page.locator('[data-testid="document-item"]');
    await expect(searchResults.first()).toBeVisible();
    
    // Test date filter
    await page.click('[data-testid="date-filter"]');
    await page.selectOption('[data-testid="date-range"]', 'last-30-days');
    await page.click('[data-testid="apply-filter"]');
    
    // Check filtered results
    await helpers.waitForLoading();
  });

  test('should handle error scenarios gracefully', async ({ page }) => {
    // Test upload of invalid file type
    await page.click('[data-testid="upload-document-btn"]');
    
    // Try to upload invalid file (simulate)
    await page.evaluate(() => {
      const input = document.querySelector('[data-testid="file-input"]') as HTMLInputElement;
      const file = new File(['invalid content'], 'test.txt', { type: 'text/plain' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      input.files = dataTransfer.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    // Check error message
    await helpers.waitForToast('Invalid file type. Please upload PDF, DOC, or DOCX files.');
    
    // Test network error handling
    await page.route('**/api/ai/analyze-document', route => route.abort());
    await page.click('[data-testid="start-analysis-btn"]');
    
    // Check error handling
    await helpers.waitForToast('Analysis failed. Please try again.');
  });

  test('should be accessible', async ({ page }) => {
    // Test keyboard navigation
    await helpers.testKeyboardNavigation('[data-testid="upload-document-btn"]', [
      '[data-testid="upload-document-btn"]',
      '[data-testid="start-analysis-btn"]',
      '[data-testid="export-report-btn"]'
    ]);
    
    // Check ARIA labels
    await expect(page.locator('[data-testid="upload-document-btn"]')).toHaveAttribute('aria-label');
    await expect(page.locator('[data-testid="analysis-progress"]')).toHaveAttribute('aria-live', 'polite');
  });
});

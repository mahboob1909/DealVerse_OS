import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers';

test.describe('Performance and Load Testing', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test('should load dashboard within acceptable time limits', async ({ page }) => {
    const startTime = Date.now();
    
    await helpers.login();
    
    // Wait for all critical elements to load
    await expect(page.locator('[data-testid="dashboard-header"]')).toBeVisible();
    await expect(page.locator('[data-testid="stats-overview"]')).toBeVisible();
    await expect(page.locator('[data-testid="recent-activity"]')).toBeVisible();
    
    const loadTime = Date.now() - startTime;
    
    // Dashboard should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    console.log(`Dashboard load time: ${loadTime}ms`);
  });

  test('should handle concurrent user sessions', async ({ browser }) => {
    const contexts = await Promise.all([
      browser.newContext(),
      browser.newContext(),
      browser.newContext(),
      browser.newContext(),
      browser.newContext(),
    ]);

    const pages = await Promise.all(contexts.map(context => context.newPage()));
    
    // Simulate 5 concurrent users logging in
    const loginPromises = pages.map(async (page, index) => {
      const helper = new TestHelpers(page);
      const startTime = Date.now();
      
      await helper.login(`user${index + 1}@dealverse.com`, 'password123');
      
      const loginTime = Date.now() - startTime;
      console.log(`User ${index + 1} login time: ${loginTime}ms`);
      
      return loginTime;
    });

    const loginTimes = await Promise.all(loginPromises);
    
    // All users should login within 5 seconds
    loginTimes.forEach(time => {
      expect(time).toBeLessThan(5000);
    });

    // Average login time should be reasonable
    const averageLoginTime = loginTimes.reduce((a, b) => a + b, 0) / loginTimes.length;
    expect(averageLoginTime).toBeLessThan(3000);

    // Cleanup
    await Promise.all(contexts.map(context => context.close()));
  });

  test('should handle large dataset rendering efficiently', async ({ page }) => {
    await helpers.login();
    await helpers.navigateToModule('diligence-navigator');
    
    // Simulate loading a large dataset
    await page.evaluate(() => {
      // Mock API response with large dataset
      window.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          documents: Array.from({ length: 1000 }, (_, i) => ({
            id: i,
            name: `Document ${i}`,
            size: Math.random() * 10000000,
            uploadDate: new Date().toISOString(),
            status: 'analyzed',
          })),
        }),
      });
    });

    const startTime = Date.now();
    
    // Trigger data load
    await page.click('[data-testid="load-all-documents"]');
    
    // Wait for virtual scrolling to render
    await expect(page.locator('[data-testid="document-list"]')).toBeVisible();
    await page.waitForFunction(() => {
      const list = document.querySelector('[data-testid="document-list"]');
      return list && list.children.length > 0;
    });

    const renderTime = Date.now() - startTime;
    
    // Large dataset should render within 2 seconds
    expect(renderTime).toBeLessThan(2000);
    console.log(`Large dataset render time: ${renderTime}ms`);
  });

  test('should maintain performance during real-time updates', async ({ page }) => {
    await helpers.login();
    
    // Monitor performance during WebSocket updates
    const performanceMetrics = [];
    
    // Start performance monitoring
    await page.addInitScript(() => {
      window.performanceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'measure') {
            window.performanceMetrics = window.performanceMetrics || [];
            window.performanceMetrics.push({
              name: entry.name,
              duration: entry.duration,
              startTime: entry.startTime,
            });
          }
        }
      });
      window.performanceObserver.observe({ entryTypes: ['measure'] });
    });

    // Simulate rapid real-time updates
    for (let i = 0; i < 50; i++) {
      await page.evaluate((index) => {
        performance.mark(`update-start-${index}`);
        
        // Simulate WebSocket message
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'activity-update',
            data: { id: index, message: `Update ${index}`, timestamp: Date.now() }
          }
        }));
        
        performance.mark(`update-end-${index}`);
        performance.measure(`update-${index}`, `update-start-${index}`, `update-end-${index}`);
      }, i);
      
      await page.waitForTimeout(100); // 100ms between updates
    }

    // Get performance metrics
    const metrics = await page.evaluate(() => window.performanceMetrics || []);
    
    // Check that updates are processed efficiently
    const averageUpdateTime = metrics.reduce((sum, metric) => sum + metric.duration, 0) / metrics.length;
    expect(averageUpdateTime).toBeLessThan(50); // Each update should take less than 50ms
    
    console.log(`Average real-time update processing time: ${averageUpdateTime}ms`);
  });

  test('should handle memory usage efficiently', async ({ page }) => {
    await helpers.login();
    
    // Monitor memory usage
    const initialMemory = await page.evaluate(() => {
      return (performance as any).memory ? {
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
      } : null;
    });

    // Perform memory-intensive operations
    await helpers.navigateToModule('diligence-navigator');
    
    // Upload and analyze multiple documents
    for (let i = 0; i < 10; i++) {
      await page.evaluate((index) => {
        // Simulate document analysis creating temporary objects
        const largeArray = new Array(100000).fill(`data-${index}`);
        window.tempData = window.tempData || [];
        window.tempData.push(largeArray);
      }, i);
      
      await page.waitForTimeout(100);
    }

    // Force garbage collection if available
    await page.evaluate(() => {
      if (window.gc) {
        window.gc();
      }
    });

    const finalMemory = await page.evaluate(() => {
      return (performance as any).memory ? {
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
      } : null;
    });

    if (initialMemory && finalMemory) {
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
      const memoryIncreasePercent = (memoryIncrease / initialMemory.usedJSHeapSize) * 100;
      
      // Memory increase should be reasonable (less than 200%)
      expect(memoryIncreasePercent).toBeLessThan(200);
      
      console.log(`Memory increase: ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB (${memoryIncreasePercent.toFixed(2)}%)`);
    }
  });

  test('should handle API response times under load', async ({ page }) => {
    await helpers.login();
    await helpers.navigateToModule('diligence-navigator');
    
    const apiResponseTimes = [];
    
    // Monitor API calls
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        const timing = response.timing();
        apiResponseTimes.push({
          url: response.url(),
          status: response.status(),
          responseTime: timing.responseEnd - timing.requestStart,
        });
      }
    });

    // Make multiple concurrent API calls
    const apiCalls = Array.from({ length: 20 }, (_, i) => 
      page.evaluate((index) => {
        return fetch(`/api/documents?page=${index}&limit=10`)
          .then(response => response.json());
      }, i)
    );

    await Promise.all(apiCalls);
    
    // Check API response times
    const averageResponseTime = apiResponseTimes.reduce((sum, call) => sum + call.responseTime, 0) / apiResponseTimes.length;
    const maxResponseTime = Math.max(...apiResponseTimes.map(call => call.responseTime));
    
    // API calls should be reasonably fast
    expect(averageResponseTime).toBeLessThan(1000); // Average < 1 second
    expect(maxResponseTime).toBeLessThan(3000); // Max < 3 seconds
    
    console.log(`Average API response time: ${averageResponseTime}ms`);
    console.log(`Max API response time: ${maxResponseTime}ms`);
  });

  test('should handle file upload performance', async ({ page }) => {
    await helpers.login();
    await helpers.navigateToModule('diligence-navigator');
    
    // Create a large test file (simulate 10MB file)
    const largeFileContent = 'x'.repeat(10 * 1024 * 1024);
    
    const startTime = Date.now();
    
    // Simulate file upload
    await page.evaluate((content) => {
      const file = new File([content], 'large-document.txt', { type: 'text/plain' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      
      const input = document.querySelector('[data-testid="file-input"]') as HTMLInputElement;
      if (input) {
        input.files = dataTransfer.files;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }, largeFileContent);

    // Wait for upload to complete
    await helpers.waitForToast('File uploaded successfully');
    
    const uploadTime = Date.now() - startTime;
    
    // Large file upload should complete within reasonable time
    expect(uploadTime).toBeLessThan(30000); // 30 seconds for 10MB file
    
    console.log(`Large file upload time: ${uploadTime}ms`);
  });

  test('should maintain UI responsiveness during heavy operations', async ({ page }) => {
    await helpers.login();
    await helpers.navigateToModule('valuation-hub');
    
    // Start a heavy computation (valuation model calculation)
    await page.click('[data-testid="complex-valuation-btn"]');
    
    // Test UI responsiveness during computation
    const responsivenessTimes = [];
    
    for (let i = 0; i < 10; i++) {
      const startTime = Date.now();
      
      // Try to interact with UI elements
      await page.hover('[data-testid="navigation-menu"]');
      await page.click('[data-testid="theme-toggle"]');
      
      const responseTime = Date.now() - startTime;
      responsivenessTimes.push(responseTime);
      
      await page.waitForTimeout(500);
    }

    const averageResponseTime = responsivenessTimes.reduce((a, b) => a + b, 0) / responsivenessTimes.length;
    
    // UI should remain responsive (interactions < 100ms)
    expect(averageResponseTime).toBeLessThan(100);
    
    console.log(`Average UI response time during heavy operation: ${averageResponseTime}ms`);
  });

  test('should handle browser resource limits gracefully', async ({ page }) => {
    await helpers.login();
    
    // Test with limited network bandwidth
    await page.route('**/*', async route => {
      // Simulate slow network (delay all requests)
      await new Promise(resolve => setTimeout(resolve, 200));
      await route.continue();
    });

    const startTime = Date.now();
    await helpers.navigateToModule('diligence-navigator');
    const navigationTime = Date.now() - startTime;
    
    // Should handle slow network gracefully
    expect(navigationTime).toBeLessThan(10000); // 10 seconds max
    
    // Check that loading indicators are shown
    await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();
    
    console.log(`Navigation time with slow network: ${navigationTime}ms`);
  });
});

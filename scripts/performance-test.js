#!/usr/bin/env node

/**
 * Performance Testing Script for DealVerse OS
 * Tests frontend and backend performance optimizations
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class PerformanceTester {
  constructor() {
    this.results = {
      timestamp: new Date().toISOString(),
      frontend: {},
      backend: {},
      summary: {}
    };
  }

  async runAllTests() {
    console.log('🚀 Starting DealVerse OS Performance Tests...\n');

    try {
      await this.testFrontendPerformance();
      await this.testBackendPerformance();
      await this.generateReport();
    } catch (error) {
      console.error('❌ Performance test failed:', error);
      process.exit(1);
    }
  }

  async testFrontendPerformance() {
    console.log('📱 Testing Frontend Performance...');
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();

    // Enable performance monitoring
    await page.addInitScript(() => {
      window.performanceMetrics = {
        navigationStart: performance.timing.navigationStart,
        loadEventEnd: 0,
        domContentLoaded: 0,
        firstPaint: 0,
        firstContentfulPaint: 0,
        largestContentfulPaint: 0,
        cumulativeLayoutShift: 0,
        firstInputDelay: 0
      };

      // Capture Core Web Vitals
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.name === 'first-paint') {
            window.performanceMetrics.firstPaint = entry.startTime;
          }
          if (entry.name === 'first-contentful-paint') {
            window.performanceMetrics.firstContentfulPaint = entry.startTime;
          }
        }
      }).observe({ entryTypes: ['paint'] });

      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'largest-contentful-paint') {
            window.performanceMetrics.largestContentfulPaint = entry.startTime;
          }
        }
      }).observe({ entryTypes: ['largest-contentful-paint'] });

      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            window.performanceMetrics.cumulativeLayoutShift += entry.value;
          }
        }
      }).observe({ entryTypes: ['layout-shift'] });
    });

    try {
      // Test dashboard loading
      console.log('  📊 Testing dashboard performance...');
      const dashboardStart = Date.now();
      await page.goto('http://localhost:3000/dashboard', { waitUntil: 'networkidle' });
      const dashboardLoadTime = Date.now() - dashboardStart;

      // Get performance metrics
      const metrics = await page.evaluate(() => {
        const timing = performance.timing;
        return {
          ...window.performanceMetrics,
          domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
          loadEventEnd: timing.loadEventEnd - timing.navigationStart,
          totalLoadTime: timing.loadEventEnd - timing.navigationStart
        };
      });

      // Test virtual scrolling performance
      console.log('  📜 Testing virtual scrolling...');
      const scrollStart = Date.now();
      
      // Simulate scrolling through large list
      for (let i = 0; i < 10; i++) {
        await page.evaluate(() => {
          const scrollContainer = document.querySelector('[data-testid="virtual-scroll"]');
          if (scrollContainer) {
            scrollContainer.scrollTop += 500;
          }
        });
        await page.waitForTimeout(100);
      }
      
      const scrollTime = Date.now() - scrollStart;

      // Test bundle size
      console.log('  📦 Analyzing bundle size...');
      const bundleMetrics = await page.evaluate(() => {
        const resources = performance.getEntriesByType('resource');
        const jsResources = resources.filter(r => r.name.includes('.js'));
        const cssResources = resources.filter(r => r.name.includes('.css'));
        
        return {
          totalJSSize: jsResources.reduce((sum, r) => sum + (r.transferSize || 0), 0),
          totalCSSSize: cssResources.reduce((sum, r) => sum + (r.transferSize || 0), 0),
          resourceCount: resources.length,
          jsResourceCount: jsResources.length,
          cssResourceCount: cssResources.length
        };
      });

      // Memory usage test
      console.log('  🧠 Testing memory usage...');
      const memoryMetrics = await page.evaluate(() => {
        if ('memory' in performance) {
          return {
            usedJSHeapSize: performance.memory.usedJSHeapSize,
            totalJSHeapSize: performance.memory.totalJSHeapSize,
            jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
          };
        }
        return null;
      });

      this.results.frontend = {
        dashboardLoadTime,
        scrollPerformance: scrollTime,
        coreWebVitals: {
          firstContentfulPaint: metrics.firstContentfulPaint,
          largestContentfulPaint: metrics.largestContentfulPaint,
          cumulativeLayoutShift: metrics.cumulativeLayoutShift,
          firstInputDelay: metrics.firstInputDelay
        },
        loadMetrics: {
          domContentLoaded: metrics.domContentLoaded,
          totalLoadTime: metrics.totalLoadTime
        },
        bundleMetrics,
        memoryMetrics
      };

      console.log('  ✅ Frontend tests completed');

    } catch (error) {
      console.error('  ❌ Frontend test error:', error);
      this.results.frontend.error = error.message;
    } finally {
      await browser.close();
    }
  }

  async testBackendPerformance() {
    console.log('🔧 Testing Backend Performance...');

    try {
      // Test API response times
      console.log('  🌐 Testing API endpoints...');
      const apiTests = [
        { name: 'Dashboard Analytics', url: 'http://localhost:8000/api/v1/analytics/dashboard' },
        { name: 'Deals List', url: 'http://localhost:8000/api/v1/deals?limit=50' },
        { name: 'Performance Metrics', url: 'http://localhost:8000/api/v1/performance/metrics' },
        { name: 'Database Health', url: 'http://localhost:8000/api/v1/performance/database/health' }
      ];

      const apiResults = {};
      
      for (const test of apiTests) {
        const start = Date.now();
        try {
          const response = await fetch(test.url, {
            headers: { 'Authorization': 'Bearer test-token' }
          });
          const responseTime = Date.now() - start;
          
          apiResults[test.name] = {
            responseTime,
            status: response.status,
            size: parseInt(response.headers.get('content-length') || '0'),
            cached: response.headers.get('x-cache') === 'HIT'
          };
        } catch (error) {
          apiResults[test.name] = {
            error: error.message,
            responseTime: Date.now() - start
          };
        }
      }

      // Test database performance
      console.log('  🗄️ Testing database performance...');
      const dbStart = Date.now();
      const dbHealthResponse = await fetch('http://localhost:8000/api/v1/performance/database/health');
      const dbHealth = await dbHealthResponse.json();
      const dbTestTime = Date.now() - dbStart;

      // Test cache performance
      console.log('  💾 Testing cache performance...');
      const cacheStart = Date.now();
      const cacheResponse = await fetch('http://localhost:8000/api/v1/performance/metrics/cache');
      const cacheMetrics = await cacheResponse.json();
      const cacheTestTime = Date.now() - cacheStart;

      this.results.backend = {
        apiPerformance: apiResults,
        databaseHealth: {
          ...dbHealth,
          testTime: dbTestTime
        },
        cachePerformance: {
          ...cacheMetrics,
          testTime: cacheTestTime
        }
      };

      console.log('  ✅ Backend tests completed');

    } catch (error) {
      console.error('  ❌ Backend test error:', error);
      this.results.backend.error = error.message;
    }
  }

  async generateReport() {
    console.log('📊 Generating Performance Report...');

    // Calculate summary scores
    const frontend = this.results.frontend;
    const backend = this.results.backend;

    // Frontend performance score (0-100)
    let frontendScore = 100;
    if (frontend.coreWebVitals) {
      if (frontend.coreWebVitals.firstContentfulPaint > 2500) frontendScore -= 20;
      if (frontend.coreWebVitals.largestContentfulPaint > 4000) frontendScore -= 20;
      if (frontend.coreWebVitals.cumulativeLayoutShift > 0.25) frontendScore -= 20;
    }
    if (frontend.dashboardLoadTime > 3000) frontendScore -= 20;
    if (frontend.bundleMetrics?.totalJSSize > 1024 * 1024) frontendScore -= 20; // 1MB

    // Backend performance score (0-100)
    let backendScore = 100;
    if (backend.apiPerformance) {
      const avgResponseTime = Object.values(backend.apiPerformance)
        .filter(result => !result.error)
        .reduce((sum, result) => sum + result.responseTime, 0) / 
        Object.keys(backend.apiPerformance).length;
      
      if (avgResponseTime > 1000) backendScore -= 30;
      else if (avgResponseTime > 500) backendScore -= 15;
    }

    this.results.summary = {
      frontendScore: Math.max(0, frontendScore),
      backendScore: Math.max(0, backendScore),
      overallScore: Math.max(0, (frontendScore + backendScore) / 2),
      recommendations: this.generateRecommendations()
    };

    // Save results
    const reportPath = path.join(__dirname, '..', 'performance-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));

    // Display summary
    this.displaySummary();
  }

  generateRecommendations() {
    const recommendations = [];
    const frontend = this.results.frontend;
    const backend = this.results.backend;

    if (frontend.coreWebVitals?.firstContentfulPaint > 2500) {
      recommendations.push('Optimize First Contentful Paint - consider code splitting and lazy loading');
    }

    if (frontend.bundleMetrics?.totalJSSize > 1024 * 1024) {
      recommendations.push('Reduce JavaScript bundle size - analyze and remove unused dependencies');
    }

    if (backend.apiPerformance) {
      const slowEndpoints = Object.entries(backend.apiPerformance)
        .filter(([name, result]) => !result.error && result.responseTime > 1000);
      
      if (slowEndpoints.length > 0) {
        recommendations.push(`Optimize slow API endpoints: ${slowEndpoints.map(([name]) => name).join(', ')}`);
      }
    }

    if (backend.cachePerformance?.hit_rate < 80) {
      recommendations.push('Improve cache hit rate - review caching strategy');
    }

    return recommendations;
  }

  displaySummary() {
    console.log('\n📈 Performance Test Results Summary');
    console.log('=====================================');
    console.log(`Overall Score: ${this.results.summary.overallScore}/100`);
    console.log(`Frontend Score: ${this.results.summary.frontendScore}/100`);
    console.log(`Backend Score: ${this.results.summary.backendScore}/100`);
    
    if (this.results.summary.recommendations.length > 0) {
      console.log('\n💡 Recommendations:');
      this.results.summary.recommendations.forEach((rec, i) => {
        console.log(`  ${i + 1}. ${rec}`);
      });
    }

    console.log('\n📄 Full report saved to: performance-report.json');
  }
}

// Run tests if called directly
if (require.main === module) {
  const tester = new PerformanceTester();
  tester.runAllTests().catch(console.error);
}

module.exports = PerformanceTester;

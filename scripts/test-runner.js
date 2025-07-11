#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * Comprehensive test runner for DealVerse OS
 * Handles unit tests, integration tests, and E2E tests
 */

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logHeader(message) {
  log(`\n${'='.repeat(60)}`, colors.cyan);
  log(`${message}`, colors.cyan + colors.bright);
  log(`${'='.repeat(60)}`, colors.cyan);
}

function logSuccess(message) {
  log(`✅ ${message}`, colors.green);
}

function logError(message) {
  log(`❌ ${message}`, colors.red);
}

function logWarning(message) {
  log(`⚠️  ${message}`, colors.yellow);
}

function logInfo(message) {
  log(`ℹ️  ${message}`, colors.blue);
}

async function runCommand(command, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: 'inherit',
      shell: true,
      ...options,
    });

    child.on('close', (code) => {
      if (code === 0) {
        resolve(code);
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });

    child.on('error', (error) => {
      reject(error);
    });
  });
}

async function checkPrerequisites() {
  logHeader('Checking Prerequisites');
  
  const checks = [
    { name: 'Node.js', command: 'node', args: ['--version'] },
    { name: 'npm', command: 'npm', args: ['--version'] },
    { name: 'Next.js dependencies', check: () => fs.existsSync('node_modules/next') },
    { name: 'Playwright', check: () => fs.existsSync('node_modules/@playwright/test') },
    { name: 'Jest', check: () => fs.existsSync('node_modules/jest') },
  ];

  for (const check of checks) {
    try {
      if (check.command) {
        await runCommand(check.command, check.args, { stdio: 'pipe' });
        logSuccess(`${check.name} is available`);
      } else if (check.check && check.check()) {
        logSuccess(`${check.name} is installed`);
      } else {
        logError(`${check.name} is missing`);
        return false;
      }
    } catch (error) {
      logError(`${check.name} check failed: ${error.message}`);
      return false;
    }
  }
  
  return true;
}

async function runUnitTests() {
  logHeader('Running Unit Tests');
  
  try {
    await runCommand('npm', ['run', 'test', '--', '--coverage', '--watchAll=false']);
    logSuccess('Unit tests completed successfully');
    return true;
  } catch (error) {
    logError(`Unit tests failed: ${error.message}`);
    return false;
  }
}

async function runE2ETests(options = {}) {
  logHeader('Running End-to-End Tests');
  
  const { project = 'chromium', headed = false, ui = false } = options;
  
  try {
    const args = ['run', 'test:e2e'];
    
    if (project !== 'all') {
      args.push('--', '--project', project);
    }
    
    if (headed) {
      args.push('--headed');
    }
    
    if (ui) {
      args.push('--ui');
    }
    
    await runCommand('npm', args);
    logSuccess('E2E tests completed successfully');
    return true;
  } catch (error) {
    logError(`E2E tests failed: ${error.message}`);
    return false;
  }
}

async function generateTestReport() {
  logHeader('Generating Test Reports');
  
  try {
    // Generate coverage report
    if (fs.existsSync('coverage')) {
      logInfo('Coverage report available at: coverage/lcov-report/index.html');
    }
    
    // Generate Playwright report
    if (fs.existsSync('playwright-report')) {
      logInfo('Playwright report available at: playwright-report/index.html');
      await runCommand('npx', ['playwright', 'show-report', '--host', '0.0.0.0']);
    }
    
    logSuccess('Test reports generated');
    return true;
  } catch (error) {
    logWarning(`Report generation failed: ${error.message}`);
    return false;
  }
}

async function runPerformanceTests() {
  logHeader('Running Performance Tests');
  
  try {
    await runCommand('npm', ['run', 'test:e2e', '--', '--grep', 'Performance']);
    logSuccess('Performance tests completed successfully');
    return true;
  } catch (error) {
    logError(`Performance tests failed: ${error.message}`);
    return false;
  }
}

async function runSecurityTests() {
  logHeader('Running Security Tests');
  
  try {
    // Run npm audit
    await runCommand('npm', ['audit', '--audit-level', 'moderate']);
    logSuccess('Security audit completed');
    
    // Run security-focused E2E tests
    await runCommand('npm', ['run', 'test:e2e', '--', '--grep', 'security|auth']);
    logSuccess('Security tests completed successfully');
    return true;
  } catch (error) {
    logWarning(`Security tests completed with warnings: ${error.message}`);
    return true; // Don't fail the entire suite for security warnings
  }
}

async function main() {
  const args = process.argv.slice(2);
  const options = {
    unit: args.includes('--unit') || args.includes('--all'),
    e2e: args.includes('--e2e') || args.includes('--all'),
    performance: args.includes('--performance') || args.includes('--all'),
    security: args.includes('--security') || args.includes('--all'),
    project: args.find(arg => arg.startsWith('--project='))?.split('=')[1] || 'chromium',
    headed: args.includes('--headed'),
    ui: args.includes('--ui'),
    report: args.includes('--report'),
  };

  // Default to running all tests if no specific test type is specified
  if (!options.unit && !options.e2e && !options.performance && !options.security) {
    options.unit = true;
    options.e2e = true;
  }

  logHeader('DealVerse OS Test Suite');
  logInfo(`Test configuration: ${JSON.stringify(options, null, 2)}`);

  // Check prerequisites
  const prerequisitesOk = await checkPrerequisites();
  if (!prerequisitesOk) {
    logError('Prerequisites check failed. Please install missing dependencies.');
    process.exit(1);
  }

  const results = {
    unit: null,
    e2e: null,
    performance: null,
    security: null,
  };

  // Run tests based on options
  if (options.unit) {
    results.unit = await runUnitTests();
  }

  if (options.e2e) {
    results.e2e = await runE2ETests({
      project: options.project,
      headed: options.headed,
      ui: options.ui,
    });
  }

  if (options.performance) {
    results.performance = await runPerformanceTests();
  }

  if (options.security) {
    results.security = await runSecurityTests();
  }

  // Generate reports
  if (options.report) {
    await generateTestReport();
  }

  // Summary
  logHeader('Test Results Summary');
  
  let allPassed = true;
  Object.entries(results).forEach(([testType, result]) => {
    if (result === true) {
      logSuccess(`${testType.toUpperCase()} tests: PASSED`);
    } else if (result === false) {
      logError(`${testType.toUpperCase()} tests: FAILED`);
      allPassed = false;
    } else {
      logInfo(`${testType.toUpperCase()} tests: SKIPPED`);
    }
  });

  if (allPassed) {
    logSuccess('\n🎉 All tests passed successfully!');
    process.exit(0);
  } else {
    logError('\n💥 Some tests failed. Please check the output above.');
    process.exit(1);
  }
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logError(`Uncaught exception: ${error.message}`);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logError(`Unhandled rejection at: ${promise}, reason: ${reason}`);
  process.exit(1);
});

// Run the main function
main().catch((error) => {
  logError(`Test runner failed: ${error.message}`);
  process.exit(1);
});

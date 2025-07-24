#!/bin/bash
# Custom build script to handle npm warnings

# Set environment variables to suppress warnings
export NPM_CONFIG_AUDIT=false
export NPM_CONFIG_FUND=false
export NPM_CONFIG_LOGLEVEL=error
export NPM_CONFIG_PROGRESS=false

# Install dependencies silently
npm install --silent --no-audit --no-fund 2>/dev/null || npm install --legacy-peer-deps --silent --no-audit --no-fund

# Build the application
next build

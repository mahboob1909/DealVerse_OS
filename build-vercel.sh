#!/bin/bash

# Vercel Build Script - Suppress all npm warnings and deprecation messages
# This script ensures a clean build output on Vercel by suppressing npm warnings

set -e

echo "Starting Vercel build with warning suppression..."

# Set environment variables to suppress npm warnings
export NPM_CONFIG_AUDIT=false
export NPM_CONFIG_FUND=false
export NPM_CONFIG_LOGLEVEL=silent
export NPM_CONFIG_PROGRESS=false
export NPM_CONFIG_UPDATE_NOTIFIER=false
export NPM_CONFIG_OPTIONAL=false
export DISABLE_OPENCOLLECTIVE=true
export ADBLOCK=true
export NODE_OPTIONS="--no-deprecation --no-warnings --disable-warning=ExperimentalWarning"
export NODE_NO_WARNINGS=1
export CI=true

# Function to run npm install with maximum warning suppression
install_dependencies() {
    echo "Installing dependencies with warning suppression..."
    
    # Try multiple approaches to suppress warnings
    npm install \
        --silent \
        --no-audit \
        --no-fund \
        --loglevel=silent \
        --no-warnings \
        --no-optional \
        --no-progress \
        --no-update-notifier \
        2>/dev/null || {
        echo "Fallback install method..."
        npm install --silent --no-audit --no-fund --loglevel=error 2>/dev/null || {
            echo "Final fallback install..."
            npm install --loglevel=error
        }
    }
}

# Function to run the build with warning suppression
run_build() {
    echo "Running Next.js build with warning suppression..."
    
    # Suppress stderr to hide deprecation warnings, but allow build errors through
    npm run build 2>/dev/null || {
        echo "Build failed, running with error output..."
        npm run build
    }
}

# Main execution
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

# Install dependencies
install_dependencies

# Run the build
run_build

echo "Build completed successfully!"

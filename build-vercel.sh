#!/bin/bash

# Vercel Build Script - Suppress all npm warnings and deprecation messages
# This script ensures a clean build output on Vercel by suppressing npm warnings

set -e

echo "Starting Vercel build with comprehensive warning suppression..."

# Set comprehensive environment variables to suppress all warnings
export NPM_CONFIG_AUDIT=false
export NPM_CONFIG_FUND=false
export NPM_CONFIG_LOGLEVEL=silent
export NPM_CONFIG_PROGRESS=false
export NPM_CONFIG_UPDATE_NOTIFIER=false
export NPM_CONFIG_OPTIONAL=false
export NPM_CONFIG_WARNINGS=false
export NPM_CONFIG_LEGACY_PEER_DEPS=true
export DISABLE_OPENCOLLECTIVE=true
export ADBLOCK=true
export NODE_OPTIONS="--no-deprecation --no-warnings --disable-warning=ExperimentalWarning --max-old-space-size=4096"
export NODE_NO_WARNINGS=1
export CI=true
export NEXT_TELEMETRY_DISABLED=1
export HUSKY=0
export SUPPRESS_NO_CONFIG_WARNING=true
export NO_UPDATE_NOTIFIER=true

# Function to run npm install with maximum warning suppression
install_dependencies() {
    echo "Installing dependencies with comprehensive warning suppression..."

    # Force clean install to avoid cached warnings
    if [ -f "package-lock.json" ]; then
        echo "Using npm ci for clean install..."
        npm ci \
            --silent \
            --no-audit \
            --no-fund \
            --loglevel=silent \
            --no-warnings \
            --no-optional \
            --no-progress \
            --no-update-notifier \
            --legacy-peer-deps \
            2>/dev/null || {
            echo "Fallback to npm install..."
            npm install \
                --silent \
                --no-audit \
                --no-fund \
                --loglevel=silent \
                --no-warnings \
                --no-optional \
                --no-progress \
                --no-update-notifier \
                --legacy-peer-deps \
                2>/dev/null || {
                echo "Final fallback install..."
                npm install --loglevel=error --legacy-peer-deps
            }
        }
    else
        echo "No package-lock.json found, using npm install..."
        npm install \
            --silent \
            --no-audit \
            --no-fund \
            --loglevel=silent \
            --no-warnings \
            --no-optional \
            --no-progress \
            --no-update-notifier \
            --legacy-peer-deps \
            2>/dev/null || {
            echo "Fallback install method..."
            npm install --loglevel=error --legacy-peer-deps
        }
    fi
}

# Function to run the build with comprehensive warning suppression
run_build() {
    echo "Running Next.js build with comprehensive warning suppression..."

    # Use the build:vercel script which has enhanced warning suppression
    npm run build:vercel 2>/dev/null || {
        echo "Build:vercel failed, trying standard build with warning suppression..."
        npm run build 2>/dev/null || {
            echo "Build failed, running with minimal error output..."
            npm run build
        }
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

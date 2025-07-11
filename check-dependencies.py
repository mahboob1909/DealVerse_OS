#!/usr/bin/env python3
"""
Dependency Checker for DealVerse OS
Checks if all required packages are installed
"""

import sys
import subprocess
from pathlib import Path

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Check and install missing dependencies"""
    print("🔍 Checking DealVerse OS Dependencies...")
    print("=" * 50)
    
    # Required packages for Neon setup
    required_packages = [
        "asyncpg",
        "fastapi", 
        "uvicorn",
        "sqlalchemy",
        "psycopg2-binary",
        "pydantic",
        "python-jose",
        "passlib",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if check_package(package):
            print(f"✅ {package}")
        else:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Found {len(missing_packages)} missing packages")
        print("🔧 Installing missing packages...")
        
        for package in missing_packages:
            print(f"📦 Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
        
        print("\n🎉 Dependency installation complete!")
        print("🔄 You can now run: python neon_setup.py")
    else:
        print("\n✅ All dependencies are installed!")
        print("🚀 You can run: python neon_setup.py")

if __name__ == "__main__":
    main()

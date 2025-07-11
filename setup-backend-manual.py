#!/usr/bin/env python3
"""
Manual Backend Setup for DealVerse OS
Handles dependency conflicts and version issues
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def run_command(command, cwd=None, shell=True):
    """Run a command and return success status"""
    try:
        print(f"🔄 Running: {command}")
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Success: {command}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {command}")
        print(f"Error: {e.stderr}")
        return False, e.stderr


def setup_backend():
    """Set up backend with error handling"""
    print("🚀 Manual Backend Setup for DealVerse OS")
    print("=" * 50)
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Step 1: Update pip first
    print("\n📦 Step 1: Updating pip...")
    success, output = run_command("python -m pip install --upgrade pip")
    if not success:
        print("⚠️  Pip update failed, continuing anyway...")
    
    # Step 2: Remove old virtual environment if it exists
    venv_dir = backend_dir / "venv"
    if venv_dir.exists():
        print("\n🗑️  Step 2: Removing old virtual environment...")
        try:
            import shutil
            shutil.rmtree(venv_dir)
            print("✅ Old virtual environment removed")
        except Exception as e:
            print(f"⚠️  Could not remove old venv: {e}")
    
    # Step 3: Create new virtual environment
    print("\n🏗️  Step 3: Creating new virtual environment...")
    success, output = run_command("python -m venv venv", cwd=backend_dir)
    if not success:
        print("❌ Failed to create virtual environment")
        return False
    
    # Step 4: Determine activation script
    if os.name == 'nt':  # Windows
        python_exe = backend_dir / "venv" / "Scripts" / "python.exe"
        pip_exe = backend_dir / "venv" / "Scripts" / "pip.exe"
    else:  # Linux/Mac
        python_exe = backend_dir / "venv" / "bin" / "python"
        pip_exe = backend_dir / "venv" / "bin" / "pip"
    
    # Step 5: Upgrade pip in virtual environment
    print("\n📦 Step 4: Upgrading pip in virtual environment...")
    success, output = run_command(f'"{python_exe}" -m pip install --upgrade pip')
    if not success:
        print("⚠️  Pip upgrade failed, continuing...")
    
    # Step 6: Install core dependencies first
    print("\n📥 Step 5: Installing core dependencies...")
    core_packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "sqlalchemy==2.0.23",
        "psycopg2-binary==2.9.9",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0"
    ]
    
    for package in core_packages:
        print(f"📦 Installing {package}...")
        success, output = run_command(f'"{pip_exe}" install {package}')
        if not success:
            print(f"⚠️  Failed to install {package}, trying without version...")
            package_name = package.split("==")[0]
            success, output = run_command(f'"{pip_exe}" install {package_name}')
            if not success:
                print(f"❌ Could not install {package_name}")
    
    # Step 7: Install remaining dependencies
    print("\n📥 Step 6: Installing remaining dependencies...")
    remaining_packages = [
        "asyncpg",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "httpx",
        "structlog"
    ]
    
    for package in remaining_packages:
        print(f"📦 Installing {package}...")
        success, output = run_command(f'"{pip_exe}" install {package}')
        if not success:
            print(f"⚠️  Failed to install {package}")
    
    # Step 8: Create .env file
    print("\n⚙️  Step 7: Setting up environment file...")
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
    
    # Step 9: Test imports
    print("\n🧪 Step 8: Testing imports...")
    test_imports = [
        "fastapi",
        "uvicorn", 
        "sqlalchemy",
        "psycopg2",
        "asyncpg",
        "pydantic",
        "dotenv"
    ]
    
    failed_imports = []
    for module in test_imports:
        success, output = run_command(f'"{python_exe}" -c "import {module}; print(f\'{module} OK\')"')
        if not success:
            failed_imports.append(module)
    
    if failed_imports:
        print(f"⚠️  Some imports failed: {failed_imports}")
        print("🔧 You may need to install these manually")
    else:
        print("✅ All core imports successful!")
    
    print("\n🎉 Backend setup completed!")
    print(f"🐍 Python executable: {python_exe}")
    print(f"📦 Pip executable: {pip_exe}")
    
    return True


def test_neon_connection():
    """Test Neon database connection"""
    print("\n🔍 Testing Neon database connection...")
    
    backend_dir = Path("backend")
    if os.name == 'nt':  # Windows
        python_exe = backend_dir / "venv" / "Scripts" / "python.exe"
    else:  # Linux/Mac
        python_exe = backend_dir / "venv" / "bin" / "python"
    
    # Test with simple connection
    test_script = '''
import os
import sys
sys.path.append("app")

try:
    from app.core.config import settings
    print("✅ Settings loaded")
    
    if settings.NEON_DATABASE_URL:
        print("✅ Neon URL configured")
        
        import psycopg2
        conn = psycopg2.connect(settings.NEON_DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database connected: {version[:50]}...")
        cursor.close()
        conn.close()
        print("🎉 Neon connection test passed!")
    else:
        print("⚠️  No Neon URL found in .env file")
        print("Please update your .env file with NEON_DATABASE_URL")
        
except Exception as e:
    print(f"❌ Connection test failed: {e}")
    print("Please check your Neon connection string")
'''
    
    # Write test script to file
    test_file = backend_dir / "test_connection.py"
    with open(test_file, 'w') as f:
        f.write(test_script)
    
    # Run test
    success, output = run_command(f'"{python_exe}" test_connection.py', cwd=backend_dir)
    
    # Clean up test file
    test_file.unlink()
    
    return success


def main():
    """Main setup function"""
    if not setup_backend():
        print("\n❌ Backend setup failed")
        return False
    
    print("\n" + "="*50)
    print("🎯 Next Steps:")
    print("1. Update your backend/.env file with your Neon connection string")
    print("2. Run: python test-neon-connection.py")
    print("3. Start backend: cd backend && venv\\Scripts\\python -m uvicorn app.main:app --reload")
    print("4. Start frontend: npm run dev")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🔧 If you continue having issues:")
        print("1. Make sure you have Python 3.8+ installed")
        print("2. Try running as administrator")
        print("3. Check your internet connection")
        print("4. Consider using a different Python version")

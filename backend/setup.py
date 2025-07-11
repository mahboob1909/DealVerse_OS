"""
Setup script for DealVerse OS Backend
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, cwd: str = None) -> bool:
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(
            command.split(),
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False


def setup_backend():
    """Setup the backend environment"""
    print("🚀 Setting up DealVerse OS Backend...")
    
    # Check if Python 3.11+ is available
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 11:
        print("❌ Python 3.11+ is required")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor} detected")
    
    # Create virtual environment
    print("\n📦 Creating virtual environment...")
    if not run_command("python -m venv venv"):
        return False
    
    # Activate virtual environment and install dependencies
    print("\n📥 Installing dependencies...")
    venv_python = "venv/Scripts/python" if os.name == "nt" else "venv/bin/python"
    venv_pip = "venv/Scripts/pip" if os.name == "nt" else "venv/bin/pip"
    
    if not run_command(f"{venv_pip} install --upgrade pip"):
        return False
    
    if not run_command(f"{venv_pip} install -r requirements.txt"):
        return False
    
    # Create .env file if it doesn't exist
    print("\n⚙️ Setting up environment configuration...")
    if not Path(".env").exists():
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from .env.example")
            print("⚠️  Please update .env file with your configuration")
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    
    print("\n🎉 Backend setup completed successfully!")
    print("\nNext steps:")
    print("1. Update .env file with your database and API keys")
    print("2. Set up your Neon PostgreSQL database")
    print("3. Run: python -m app.db.init_db to initialize the database")
    print("4. Run: uvicorn app.main:app --reload to start the development server")
    
    return True


def setup_docker():
    """Setup Docker environment"""
    print("\n🐳 Setting up Docker environment...")
    
    # Check if Docker is available
    if not run_command("docker --version"):
        print("❌ Docker is not installed or not available")
        return False
    
    if not run_command("docker-compose --version"):
        print("❌ Docker Compose is not installed or not available")
        return False
    
    print("✅ Docker and Docker Compose are available")
    
    # Build and start services
    print("\n🏗️ Building Docker containers...")
    if not run_command("docker-compose build"):
        return False
    
    print("\n🚀 Starting services...")
    if not run_command("docker-compose up -d db redis"):
        return False
    
    print("✅ Database and Redis services started")
    print("\nTo start the full application:")
    print("docker-compose up")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup DealVerse OS Backend")
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Setup Docker environment instead of local development"
    )
    
    args = parser.parse_args()
    
    if args.docker:
        success = setup_docker()
    else:
        success = setup_backend()
    
    if not success:
        sys.exit(1)

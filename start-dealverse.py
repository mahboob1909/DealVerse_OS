#!/usr/bin/env python3
"""
DealVerse OS Startup Script
Helps users start both frontend and backend services
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path


def run_command(command, cwd=None, background=False):
    """Run a command and return the process"""
    try:
        if background:
            return subprocess.Popen(
                command.split(),
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            result = subprocess.run(
                command.split(),
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True
            )
            return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None


def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except:
        print("❌ Node.js not found. Please install Node.js 18+")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        print(f"✅ npm: {result.stdout.strip()}")
    except:
        print("❌ npm not found")
        return False
    
    return True


def setup_backend():
    """Set up the backend environment"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Check if virtual environment exists
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("📦 Creating virtual environment...")
        result = run_command("python -m venv venv", cwd=backend_dir)
        if not result:
            return False
    
    # Install dependencies
    print("📥 Installing Python dependencies...")
    pip_cmd = str(venv_dir / "Scripts" / "pip") if os.name == "nt" else str(venv_dir / "bin" / "pip")
    result = run_command(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir)
    if not result:
        return False
    
    # Check .env file
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚙️ Creating .env file...")
        example_env = backend_dir / ".env.example"
        if example_env.exists():
            import shutil
            shutil.copy(example_env, env_file)
            print("✅ Created .env file from .env.example")
            print("⚠️  Please update .env file with your Neon database URL")
        else:
            print("❌ .env.example not found")
            return False
    
    return True


def setup_frontend():
    """Set up the frontend environment"""
    print("\n🔧 Setting up frontend...")
    
    # Install dependencies
    print("📥 Installing Node.js dependencies...")
    result = run_command("npm install")
    if not result:
        return False
    
    # Check .env.local file
    env_file = Path(".env.local")
    if not env_file.exists():
        print("⚙️ Creating .env.local file...")
        example_env = Path(".env.local.example")
        if example_env.exists():
            import shutil
            shutil.copy(example_env, env_file)
            print("✅ Created .env.local file")
        else:
            print("❌ .env.local.example not found")
            return False
    
    return True


def start_services():
    """Start both backend and frontend services"""
    print("\n🚀 Starting services...")
    
    # Start backend
    print("🔄 Starting backend server...")
    backend_dir = Path("backend")
    python_cmd = str(backend_dir / "venv" / "Scripts" / "python") if os.name == "nt" else str(backend_dir / "venv" / "bin" / "python")
    
    backend_process = run_command(
        f"{python_cmd} -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
        cwd=backend_dir,
        background=True
    )
    
    if not backend_process:
        print("❌ Failed to start backend")
        return False
    
    print("✅ Backend started on http://localhost:8000")
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    print("🔄 Starting frontend server...")
    frontend_process = run_command("npm run dev", background=True)
    
    if not frontend_process:
        print("❌ Failed to start frontend")
        backend_process.terminate()
        return False
    
    print("✅ Frontend started on http://localhost:3000")
    
    # Wait for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    # Open browser
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:3000")
    
    print("\n🎉 DealVerse OS is now running!")
    print("\n📋 Service URLs:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/api/v1/docs")
    
    print("\n👤 Demo Login Credentials:")
    print("   Admin: admin@dealverse.com / changethis")
    print("   Manager: manager@dealverse.com / manager123")
    print("   Analyst: analyst@dealverse.com / analyst123")
    
    print("\n⚠️  Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Services stopped")


def main():
    """Main function"""
    print("🚀 DealVerse OS Startup Script")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed")
        sys.exit(1)
    
    # Start services
    start_services()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Complete DealVerse OS Setup Script
Guides users through the entire setup process including Neon database
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)


def print_step(step_num, title):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {title}")
    print("-" * 40)


def wait_for_user():
    """Wait for user to press Enter"""
    input("\nPress Enter to continue...")


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


def setup_neon_database():
    """Guide user through Neon database setup"""
    print_step(1, "Neon Database Setup")
    
    print("🎯 We'll set up your PostgreSQL database on Neon.")
    print("\n📋 What you need to do:")
    print("1. Go to https://neon.com and create an account")
    print("2. Create a new project named 'dealverse-os'")
    print("3. Copy the connection string")
    
    webbrowser.open("https://neon.com")
    print("\n🌐 Opening Neon website in your browser...")
    
    wait_for_user()
    
    # Get connection string from user
    print("\n🔗 Please paste your Neon connection string:")
    print("(It should look like: postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dealverse_db)")
    
    while True:
        connection_string = input("\nNeon Connection String: ").strip()
        if connection_string.startswith("postgresql://") and "neon.tech" in connection_string:
            break
        else:
            print("❌ Invalid connection string. Please try again.")
    
    # Update .env file
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    
    # Create .env from template if it doesn't exist
    if not env_file.exists():
        example_env = backend_dir / ".env.example"
        if example_env.exists():
            import shutil
            shutil.copy(example_env, env_file)
    
    # Update the connection string
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace the NEON_DATABASE_URL line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('NEON_DATABASE_URL='):
                lines[i] = f'NEON_DATABASE_URL={connection_string}'
                break
        else:
            # Add the line if it doesn't exist
            lines.append(f'NEON_DATABASE_URL={connection_string}')
        
        with open(env_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ Updated .env file with Neon connection string")
    
    return connection_string


def setup_backend():
    """Set up the backend environment"""
    print_step(2, "Backend Setup")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create virtual environment
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("📦 Creating Python virtual environment...")
        result = run_command("python -m venv venv", cwd=backend_dir)
        if not result:
            return False
        print("✅ Virtual environment created")
    
    # Install dependencies
    print("📥 Installing Python dependencies...")
    pip_cmd = str(venv_dir / "Scripts" / "pip") if os.name == "nt" else str(venv_dir / "bin" / "pip")
    result = run_command(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir)
    if not result:
        return False
    print("✅ Python dependencies installed")
    
    return True


def test_database_connection():
    """Test the database connection and initialize"""
    print_step(3, "Database Connection Test")
    
    backend_dir = Path("backend")
    python_cmd = str(backend_dir / "venv" / "Scripts" / "python") if os.name == "nt" else str(backend_dir / "venv" / "bin" / "python")
    
    print("🔍 Testing Neon database connection...")
    result = run_command(f"{python_cmd} neon_setup.py", cwd=backend_dir)
    
    if result:
        print("✅ Database connection successful!")
        print("✅ Database schema initialized!")
        print("✅ Sample data created!")
        return True
    else:
        print("❌ Database connection failed")
        return False


def setup_frontend():
    """Set up the frontend environment"""
    print_step(4, "Frontend Setup")
    
    print("📥 Installing Node.js dependencies...")
    result = run_command("npm install")
    if not result:
        return False
    print("✅ Node.js dependencies installed")
    
    # Create .env.local
    env_file = Path(".env.local")
    if not env_file.exists():
        example_env = Path(".env.local.example")
        if example_env.exists():
            import shutil
            shutil.copy(example_env, env_file)
            print("✅ Created .env.local file")
    
    return True


def start_services():
    """Start both services"""
    print_step(5, "Starting Services")
    
    backend_dir = Path("backend")
    python_cmd = str(backend_dir / "venv" / "Scripts" / "python") if os.name == "nt" else str(backend_dir / "venv" / "bin" / "python")
    
    print("🔄 Starting backend server...")
    backend_process = run_command(
        f"{python_cmd} -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
        cwd=backend_dir,
        background=True
    )
    
    if not backend_process:
        print("❌ Failed to start backend")
        return False
    
    print("✅ Backend started on http://localhost:8000")
    time.sleep(3)
    
    print("🔄 Starting frontend server...")
    frontend_process = run_command("npm run dev", background=True)
    
    if not frontend_process:
        print("❌ Failed to start frontend")
        backend_process.terminate()
        return False
    
    print("✅ Frontend started on http://localhost:3000")
    time.sleep(5)
    
    return backend_process, frontend_process


def show_completion_info():
    """Show completion information"""
    print_header("🎉 DealVerse OS Setup Complete!")
    
    print("\n🌐 Application URLs:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/api/v1/docs")
    
    print("\n👤 Demo Login Credentials:")
    print("   Admin: admin@dealverse.com / changethis")
    print("   Manager: manager@dealverse.com / manager123")
    print("   Analyst: analyst@dealverse.com / analyst123")
    print("   Associate: associate@dealverse.com / associate123")
    print("   VP: vp@dealverse.com / vp123")
    
    print("\n🎯 Next Steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Login with one of the demo accounts")
    print("3. Explore the 5 core modules:")
    print("   - Prospect AI")
    print("   - Diligence Navigator")
    print("   - Valuation & Modeling Hub")
    print("   - Compliance Guardian")
    print("   - PitchCraft Suite")
    print("4. Create your first deal, client, or document")
    
    print("\n⚠️  Press Ctrl+C to stop all services")
    
    # Open browser
    print("\n🌐 Opening DealVerse OS in your browser...")
    webbrowser.open("http://localhost:3000")


def main():
    """Main setup function"""
    print_header("DealVerse OS Complete Setup")
    
    print("🎯 This script will guide you through setting up DealVerse OS")
    print("📋 We'll cover:")
    print("   1. Neon Database Setup")
    print("   2. Backend Environment")
    print("   3. Database Connection Test")
    print("   4. Frontend Environment")
    print("   5. Starting Services")
    
    wait_for_user()
    
    # Step 1: Neon Database Setup
    connection_string = setup_neon_database()
    
    # Step 2: Backend Setup
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Step 3: Test Database Connection
    if not test_database_connection():
        print("❌ Database connection failed")
        sys.exit(1)
    
    # Step 4: Frontend Setup
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    # Step 5: Start Services
    processes = start_services()
    if not processes:
        print("❌ Failed to start services")
        sys.exit(1)
    
    backend_process, frontend_process = processes
    
    # Show completion info
    show_completion_info()
    
    try:
        # Keep services running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Services stopped")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Setup script for the Data Scientist AI Agent project.
This script sets up the virtual environment and installs dependencies.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📋 {description}...")
    try:
        if platform.system() == "Windows":
            # On Windows, use shell=True to handle batch files
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        
        if result.stdout:
            print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Data Scientist AI Agent...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required. Current version:", sys.version)
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Create virtual environment
    venv_path = "venv"
    if not os.path.exists(venv_path):
        if not run_command("python -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation command based on OS
    if platform.system() == "Windows":
        activate_cmd = r"venv\Scripts\activate.bat && "
        pip_cmd = "pip"
    else:
        activate_cmd = "source venv/bin/activate && "
        pip_cmd = "pip"
    
    # Install dependencies
    install_cmd = f"{activate_cmd}{pip_cmd} install -r requirements.txt"
    if not run_command(install_cmd, "Installing dependencies"):
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set up your Google API key:")
    print("   - Run: python setup_api_key.py")
    print("   - Or manually create a .env file with GOOGLE_API_KEY")
    print("\n2. Run the application:")
    if platform.system() == "Windows":
        print("   - run_venv.bat")
    else:
        print("   - ./run_venv.sh")
    print("   - Or: streamlit run src/app.py (after activating venv)")
    print("\n3. Access the app at: http://localhost:8501")
    print("\n📚 For more help, see:")
    print("   - README.md")
    print("   - SETUP_GUIDE.md")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Setup script for creating a virtual environment and installing dependencies
for the Military Image Classification System.
"""

import os
import subprocess
import sys
import venv

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{description}")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("[OK] Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed: {e.stderr}")
        return False

def main():
    print("=== Military Image Classification System - Environment Setup ===")

    # Check Python version
    if sys.version_info < (3, 8):
        print(f"[ERROR] Python 3.8+ required. You have Python {sys.version}")
        return

    print(f"[OK] Python {sys.version} detected")

    # Create virtual environment
    venv_path = "venv"
    if os.path.exists(venv_path):
        print(f"Virtual environment already exists at {venv_path}")
        print("Using existing virtual environment")
    else:
        print(f"\nCreating virtual environment at {venv_path}...")
        venv.create(venv_path, with_pip=True)
        print("[OK] Virtual environment created")

    # Get paths for the virtual environment
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_path, 'Scripts', 'pip')
        python_path = os.path.join(venv_path, 'Scripts', 'python')
    else:  # Unix/Linux
        pip_path = os.path.join(venv_path, 'bin', 'pip')
        python_path = os.path.join(venv_path, 'bin', 'python')

    # Upgrade pip
    run_command(f'"{pip_path}" install --upgrade pip', "Upgrading pip in virtual environment...")

    # Install basic dependencies first
    print("\nInstalling basic dependencies...")
    basic_deps = ["psycopg2-binary", "Pillow", "numpy", "tqdm", "pandas"]
    for dep in basic_deps:
        if not run_command(f'"{pip_path}" install {dep}', f"Installing {dep}..."):
            return

    # Test database connection
    print("\nTesting database connection...")
    print("Note: Update database credentials in test_db_connection.py if needed")
    run_command(f'"{python_path}" test_db_connection.py', "Testing PostgreSQL connection...")

    # Set up database
    print("\nSetting up database schema...")
    run_command(f'"{python_path}" setup_database.py', "Creating database and tables...")

    # Install ML dependencies (needed for image classification)
    print("\nInstalling ML Dependencies (Large download - ~8GB)...")
    print("This is required for the image classification to work.")
    ml_deps = ["torch", "torchvision", "transformers", "accelerate"]
    for dep in ml_deps:
        if not run_command(f'"{pip_path}" install {dep}', f"Installing {dep}..."):
            print(f"Failed to install {dep}. You can try again later.")
            break
    else:
        print("\n[OK] All dependencies installed!")

    # Create activation scripts
    print("\nCreating activation shortcuts...")

    if os.name == 'nt':  # Windows
        with open('activate_venv.bat', 'w') as f:
            f.write(f'@echo off\ncall {venv_path}\\Scripts\\activate.bat\ncmd\n')
        print("[OK] Created activate_venv.bat for Windows")

        with open('run_classifier.bat', 'w') as f:
            f.write(f'@echo off\ncall {venv_path}\\Scripts\\activate.bat\npython image_classifier.py\n')
        print("[OK] Created run_classifier.bat for easy execution")
    else:  # Unix/Linux
        with open('activate_venv.sh', 'w') as f:
            f.write(f'#!/bin/bash\nsource {venv_path}/bin/activate\nexec $SHELL\n')
        os.chmod('activate_venv.sh', 0o755)
        print("[OK] Created activate_venv.sh for Linux/Mac")

        with open('run_classifier.sh', 'w') as f:
            f.write(f'#!/bin/bash\nsource {venv_path}/bin/activate\npython image_classifier.py\n')
        os.chmod('run_classifier.sh', 0o755)
        print("[OK] Created run_classifier.sh for easy execution")

    print("\n=== Setup Complete ===")
    print(f"\nTo activate the virtual environment:")
    if os.name == 'nt':
        print(f"  Double-click activate_venv.bat")
        print(f"  Or run: {venv_path}\\Scripts\\activate.bat")
    else:
        print(f"  Run: source {venv_path}/bin/activate")
        print(f"  Or run: ./activate_venv.sh")

    print(f"\nTo run the classifier:")
    if os.name == 'nt':
        print(f"  Double-click run_classifier.bat")
        print(f"  Or run: {venv_path}\\Scripts\\python image_classifier.py")
    else:
        print(f"  Run: ./run_classifier.sh")
        print(f"  Or run: {venv_path}/bin/python image_classifier.py")

    print(f"\nTo deactivate: deactivate")

if __name__ == "__main__":
    main()

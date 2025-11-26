import subprocess
import sys
import os

def setup():
    print("KyleH System Monitor - Setup Script")
    print("=" * 50)
    print()
    
    print("Step 1: Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("ERROR: Failed to install dependencies")
        print("Try running: pip install -r requirements.txt")
        return False
    
    print("\nStep 2: Creating directories...")
    os.makedirs("logs", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    print("Directories created!")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Test the monitor: python monitor.py")
    print("2. Install as service (Admin): python install_service.py")
    print()
    
    return True

if __name__ == "__main__":
    setup()

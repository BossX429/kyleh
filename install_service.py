import sys
import os
import subprocess
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def install_service():
    if not is_admin():
        print("ERROR: This script must be run as Administrator!")
        print("Right-click and select 'Run as administrator'")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("Installing KyleH System Monitor as Windows Service...")
    
    service_script = os.path.join(os.path.dirname(__file__), 'service_wrapper.py')
    
    try:
        subprocess.run([sys.executable, service_script, 'install'], check=True)
        print("\nService installed successfully!")
        print("\nStarting service...")
        subprocess.run([sys.executable, service_script, 'start'], check=True)
        print("Service started!")
        print("\nService Management Commands:")
        print(f"  Start:   python {service_script} start")
        print(f"  Stop:    python {service_script} stop")
        print(f"  Restart: python {service_script} restart")
        print(f"  Remove:  python {service_script} remove")
        print("\nCheck logs at: C:\\Projects\\kyleh\\logs\\monitor.log")
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install service: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_service()
    input("\nPress Enter to exit...")

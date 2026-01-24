"""
Quick Start Script for GameCore Monitor
Checks dependencies and launches the dashboard
"""

import sys
import subprocess
import importlib.util

def check_package(package_name):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def main():
    print("=" * 50)
    print("GameCore Monitor - Startup Check")
    print("=" * 50)
    print()
    
    # Check required packages
    required_packages = {
        'psutil': 'System monitoring',
        'streamlit': 'Dashboard UI',
        'plotly': 'Interactive charts',
        'pandas': 'Data handling',
        'GPUtil': 'GPU monitoring',
        'wmi': 'Windows hardware info'
    }
    
    missing_packages = []
    
    print("Checking dependencies...")
    for package, description in required_packages.items():
        if check_package(package):
            print(f"✓ {package} ({description})")
        else:
            print(f"✗ {package} ({description}) - MISSING")
            missing_packages.append(package)
    
    print()
    
    if missing_packages:
        print("Missing packages detected!")
        print("Run: pip install -r requirements.txt")
        print()
        
        response = input("Install missing packages now? (y/n): ")
        if response.lower() == 'y':
            print("\nInstalling packages...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("\n✓ Installation complete!")
        else:
            print("\nPlease install dependencies before running GameCore Monitor.")
            return
    
    print("\n" + "=" * 50)
    print("Starting GameCore Monitor...")
    print("=" * 50)
    print("\nDashboard will open in your browser.")
    print("Press Ctrl+C to stop the monitor.\n")
    
    # Launch Streamlit
    subprocess.run([
        sys.executable, 
        "-m", 
        "streamlit", 
        "run", 
        "app.py",
        "--theme.base", "dark"
    ])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGameCore Monitor stopped.")
    except Exception as e:
        print(f"\nError: {e}")
        input("Press Enter to exit...")

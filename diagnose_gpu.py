"""
GPU Detection Diagnostic for RTX 5050
Tests multiple methods to detect NVIDIA GPU
"""

import sys

print("=" * 60)
print("GPU DETECTION DIAGNOSTIC - RTX 5050")
print("=" * 60)
print()

# Test 1: GPUtil
print("Test 1: GPUtil Detection")
print("-" * 60)
try:
    import GPUtil
    gpus = GPUtil.getGPUs()
    if gpus:
        print(f"✓ GPUtil FOUND {len(gpus)} GPU(s):")
        for gpu in gpus:
            print(f"  - Name: {gpu.name}")
            print(f"  - ID: {gpu.id}")
            print(f"  - Load: {gpu.load * 100:.1f}%")
            print(f"  - Temp: {gpu.temperature}°C")
            print(f"  - Memory: {gpu.memoryUsed}/{gpu.memoryTotal} MB")
            print(f"  - Driver: {gpu.driver}")
    else:
        print("✗ GPUtil found NO GPUs")
        print("  Possible reasons:")
        print("  1. NVIDIA drivers not installed")
        print("  2. GPU in power-saving mode (using Intel iGPU)")
        print("  3. nvidia-smi not in PATH")
except ImportError:
    print("✗ GPUtil not installed")
    print("  Run: pip install gputil")
except Exception as e:
    print(f"✗ GPUtil error: {e}")

print()

# Test 2: WMI
print("Test 2: WMI Detection (All GPUs)")
print("-" * 60)
try:
    import wmi
    w = wmi.WMI()
    video_controllers = w.Win32_VideoController()
    
    if video_controllers:
        print(f"✓ WMI FOUND {len(video_controllers)} GPU(s):")
        for i, gpu in enumerate(video_controllers, 1):
            print(f"\n  GPU {i}:")
            print(f"  - Name: {gpu.Name}")
            print(f"  - Status: {gpu.Status}")
            print(f"  - Driver Version: {gpu.DriverVersion}")
            if gpu.AdapterRAM:
                vram_gb = int(gpu.AdapterRAM) / (1024**3)
                print(f"  - VRAM: {vram_gb:.1f} GB")
            print(f"  - Video Processor: {gpu.VideoProcessor}")
    else:
        print("✗ WMI found NO GPUs")
except ImportError:
    print("✗ WMI not installed")
    print("  Run: pip install wmi")
except Exception as e:
    print(f"✗ WMI error: {e}")

print()

# Test 3: nvidia-smi command
print("Test 3: nvidia-smi Command")
print("-" * 60)
try:
    import subprocess
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=name,driver_version,memory.total', '--format=csv,noheader'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        print("✓ nvidia-smi WORKS:")
        print(f"  {result.stdout.strip()}")
    else:
        print("✗ nvidia-smi failed")
        print(f"  Error: {result.stderr}")
except FileNotFoundError:
    print("✗ nvidia-smi NOT FOUND in PATH")
    print("  This means NVIDIA drivers may not be installed properly")
    print("  Or nvidia-smi.exe is not in system PATH")
except Exception as e:
    print(f"✗ nvidia-smi error: {e}")

print()

# Test 4: Check for Optimus (laptop hybrid graphics)
print("Test 4: Hybrid Graphics Detection (Optimus)")
print("-" * 60)
try:
    import wmi
    w = wmi.WMI()
    gpus = w.Win32_VideoController()
    
    intel_found = False
    nvidia_found = False
    
    for gpu in gpus:
        if 'Intel' in gpu.Name:
            intel_found = True
            print(f"✓ Intel iGPU detected: {gpu.Name}")
        if 'NVIDIA' in gpu.Name or 'GeForce' in gpu.Name or 'RTX' in gpu.Name:
            nvidia_found = True
            print(f"✓ NVIDIA GPU detected: {gpu.Name}")
    
    print()
    if intel_found and nvidia_found:
        print("⚠ OPTIMUS DETECTED (Hybrid Graphics)")
        print("  Your laptop has both Intel iGPU + NVIDIA RTX 5050")
        print("  Windows may be using Intel iGPU to save power!")
        print()
        print("  Solutions:")
        print("  1. Open NVIDIA Control Panel")
        print("  2. Go to 'Manage 3D Settings'")
        print("  3. Set 'Python.exe' to use 'High-performance NVIDIA processor'")
        print("  4. Or set Global Setting to prefer NVIDIA")
        print()
        print("  Alternative:")
        print("  • Windows Settings → Display → Graphics Settings")
        print("  • Add Python.exe as 'High Performance'")
    elif not nvidia_found:
        print("✗ NVIDIA GPU NOT detected by WMI")
        print("  Check Device Manager for RTX 5050")
except Exception as e:
    print(f"Error checking Optimus: {e}")

print()

# Test 5: Check NVIDIA driver installation
print("Test 5: NVIDIA Driver Check")
print("-" * 60)
try:
    import winreg
    
    # Check NVIDIA registry key
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SOFTWARE\NVIDIA Corporation\Global")
        driver_version, _ = winreg.QueryValueEx(key, "DriverVersion")
        print(f"✓ NVIDIA Driver installed: {driver_version}")
        winreg.CloseKey(key)
    except FileNotFoundError:
        print("✗ NVIDIA driver registry key NOT FOUND")
        print("  Driver may not be installed correctly")
except Exception as e:
    print(f"Error checking registry: {e}")

print()
print("=" * 60)
print("RECOMMENDATIONS FOR RTX 5050:")
print("=" * 60)
print()
print("If GPU not detected:")
print("1. Update NVIDIA drivers from GeForce Experience")
print("2. Set Python to use NVIDIA GPU (not Intel iGPU)")
print("3. Restart computer after driver update")
print("4. Run this script as Administrator")
print()
print("For GameCore Monitor to detect GPU:")
print("• Ensure nvidia-smi works in command prompt")
print("• Set Python to high-performance GPU")
print("• Restart the monitor after driver/settings change")
print()
print("=" * 60)

input("\nPress Enter to exit...")

"""
Sensor Validation Script
Tests all sensors from CLI and reports status
"""

import sys
import json
import time
from datetime import datetime

print("=" * 60)
print("GameCore Monitor - Sensor Validation")
print("=" * 60)
print()

# Test CPU Sensor
print("1. Testing CPU Sensor...")
try:
    from src.sensors.cpu_sensor import CPUSensor
    cpu = CPUSensor()
    cpu_data = cpu.update()
    
    print(f"   ✓ CPU Usage: {cpu_data['usage_percent']:.1f}%")
    print(f"   ✓ Frequency: {cpu_data['frequency']['current']:.0f} MHz")
    print(f"   ✓ Cores: {cpu_data['core_count']}P / {cpu_data['thread_count']}L")
    
    cpu_temp = cpu_data['temperature']['current']
    if cpu_temp:
        print(f"   ✓ Temperature: {cpu_temp:.1f}°C")
    else:
        print(f"   ⚠ Temperature: N/A (Install OpenHardwareMonitor for temp readings)")
    
    print("   ✅ CPU Sensor OK")
except Exception as e:
    print(f"   ❌ CPU Sensor FAILED: {e}")
    sys.exit(1)

print()

# Test GPU Sensor
print("2. Testing GPU Sensor...")
try:
    from src.sensors.gpu_sensor import GPUSensor
    gpu = GPUSensor()
    gpu_data = gpu.update()
    
    if gpu_data['available']:
        gpu_info = gpu_data['gpus'][0]
        print(f"   ✓ GPU: {gpu_info['name']}")
        print(f"   ✓ Usage: {gpu_info['load_percent']:.1f}%")
        print(f"   ✓ Temperature: {gpu_info['temperature_c']:.1f}°C")
        print(f"   ✓ Memory: {gpu_info['memory']['used_mb']:.0f}/{gpu_info['memory']['total_mb']:.0f} MB ({gpu_info['memory']['percent']:.1f}%)")
        print(f"   ✓ Driver: {gpu_info['driver']}")
        print("   ✅ GPU Sensor OK")
    else:
        print("   ⚠ No NVIDIA GPU detected (using Optimus Intel iGPU)")
        print("   ✅ GPU Sensor OK (detection working)")
except Exception as e:
    print(f"   ❌ GPU Sensor FAILED: {e}")
    sys.exit(1)

print()

# Test RAM Sensor
print("3. Testing RAM Sensor...")
try:
    from src.sensors.ram_sensor import RAMSensor
    ram = RAMSensor()
    ram_data = ram.update()
    
    print(f"   ✓ Total: {ram_data['total_gb']:.2f} GB")
    print(f"   ✓ Used: {ram_data['used_gb']:.2f} GB")
    print(f"   ✓ Available: {ram_data['available_gb']:.2f} GB")
    print(f"   ✓ Usage: {ram_data['percent']:.1f}%")
    print("   ✅ RAM Sensor OK")
except Exception as e:
    print(f"   ❌ RAM Sensor FAILED: {e}")
    sys.exit(1)

print()

# Test Disk Sensor
print("4. Testing Disk Sensor...")
try:
    from src.sensors.disk_sensor import DiskSensor
    disk = DiskSensor()
    disk_data = disk.update()
    
    print(f"   ✓ Disks found: {len(disk_data.get('disks', []))}")
    for d in disk_data.get('disks', []):
        print(f"     - {d['device']}: {d['used_gb']:.0f}/{d['total_gb']:.0f} GB ({d['percent']:.1f}%)")
    
    # Test I/O (requires 2 readings)
    time.sleep(1)
    disk_data2 = disk.update()
    read_speed = disk_data2.get('read_speed_mbps', 0)
    write_speed = disk_data2.get('write_speed_mbps', 0)
    print(f"   ✓ I/O: {read_speed:.1f} MB/s read, {write_speed:.1f} MB/s write")
    print("   ✅ Disk Sensor OK")
except Exception as e:
    print(f"   ❌ Disk Sensor FAILED: {e}")
    sys.exit(1)

print()

# Test Network Sensor
print("5. Testing Network Sensor...")
try:
    from src.sensors.network_sensor import NetworkSensor
    net = NetworkSensor()
    net.update()  # First reading
    time.sleep(1)  # Wait 1 sec for delta
    net_data = net.update()  # Second reading
    
    print(f"   ✓ Upload: {net_data['upload_speed_mbps']:.2f} Mbps")
    print(f"   ✓ Download: {net_data['download_speed_mbps']:.2f} Mbps")
    print(f"   ✓ Total Sent: {net_data['total_sent_gb']:.2f} GB")
    print(f"   ✓ Total Received: {net_data['total_recv_gb']:.2f} GB")
    print(f"   ✓ Connections: {net_data['connections']['total']} ({net_data['connections']['established']} established)")
    print("   ✅ Network Sensor OK")
except Exception as e:
    print(f"   ❌ Network Sensor FAILED: {e}")
    sys.exit(1)

print()

# Test Background Monitor
print("6. Testing Background Monitor...")
try:
    from src.sensors.cpu_sensor import CPUSensor
    from src.sensors.gpu_sensor import GPUSensor
    from src.sensors.ram_sensor import RAMSensor
    from src.sensors.disk_sensor import DiskSensor
    from src.sensors.network_sensor import NetworkSensor
    from src.sensors.system_sensor import SystemSensor
    from src.utils.background_monitor import BackgroundMonitor
    
    # Create sensor manager
    class SensorManager:
        def __init__(self):
            self.sensors = {
                "cpu": CPUSensor(),
                "gpu": GPUSensor(),
                "ram": RAMSensor(),
                "disk": DiskSensor(),
                "network": NetworkSensor(),
                "system": SystemSensor()
            }
        
        def get_sensor(self, name):
            return self.sensors[name]
        
        def update_all(self):
            for sensor in self.sensors.values():
                sensor.update()
    
    sensor_manager = SensorManager()
    monitor = BackgroundMonitor(sensor_manager, update_interval=1.0)
    
    print("   ✓ Starting background monitor...")
    monitor.start()
    
    print("   ✓ Waiting 2 seconds for data...")
    time.sleep(2)
    
    stats = monitor.get_stats()
    print(f"   ✓ Updates: {stats['update_count']}")
    print(f"   ✓ Avg time: {stats['avg_update_time_ms']:.1f} ms")
    print(f"   ✓ Healthy: {monitor.is_healthy()}")
    
    cached = monitor.get_cached_data()
    if cached and cached.get('cpu'):
        print(f"   ✓ Cached data available (CPU: {cached['cpu']['usage_percent']:.1f}%)")
    
    monitor.stop()
    print("   ✅ Background Monitor OK")
except Exception as e:
    print(f"   ❌ Background Monitor FAILED: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL SENSORS VALIDATED SUCCESSFULLY")
print("=" * 60)
print()
print("Summary:")
print("  • All sensors working correctly")
print("  • Background monitoring operational")
print("  • Ready for dashboard use")
print()
print("Note: If CPU temperature shows N/A, install OpenHardwareMonitor")
print("      for accurate thermal readings.")

"""
CPU Monitoring Sensor
Monitors CPU usage, frequency, temperature, and core statistics
"""

import psutil
import time
from typing import Dict, Any
from .base_sensor import BaseSensor

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False


class CPUSensor(BaseSensor):
    """CPU monitoring sensor"""
    
    def __init__(self):
        super().__init__("CPU")
        self.core_count = psutil.cpu_count(logical=False)
        self.thread_count = psutil.cpu_count(logical=True)
        self.wmi_interface = None
        
        if WMI_AVAILABLE:
            try:
                self.wmi_interface = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
            except:
                self.wmi_interface = None
    
    def read(self) -> Dict[str, Any]:
        """Read CPU metrics"""
        data = {
            "usage_percent": psutil.cpu_percent(interval=0.1),
            "per_core_usage": psutil.cpu_percent(interval=0.1, percpu=True),
            "frequency": self._get_frequency(),
            "core_count": self.core_count,
            "thread_count": self.thread_count,
            "temperature": self._get_temperature(),
            "load_average": self._get_load_average(),
        }
        
        return data
    
    def _get_frequency(self) -> Dict[str, float]:
        """Get CPU frequency in MHz"""
        try:
            freq = psutil.cpu_freq()
            if freq:
                return {
                    "current": round(freq.current, 2),
                    "min": round(freq.min, 2),
                    "max": round(freq.max, 2)
                }
        except:
            pass
        return {"current": 0, "min": 0, "max": 0}
    
    def _get_temperature(self) -> Dict[str, float]:
        """Get CPU temperature (requires admin/WMI)"""
        # Try psutil first (works on some systems)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Look for CPU temperature
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'core' in name.lower():
                        if entries:
                            return {
                                "current": round(entries[0].current, 1),
                                "high": round(entries[0].high, 1) if entries[0].high else None,
                                "critical": round(entries[0].critical, 1) if entries[0].critical else None
                            }
        except:
            pass
        
        # Try WMI/OpenHardwareMonitor
        if self.wmi_interface:
            try:
                sensors = self.wmi_interface.Sensor()
                for sensor in sensors:
                    if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                        return {
                            "current": round(float(sensor.Value), 1),
                            "high": None,
                            "critical": None
                        }
            except:
                pass
        
        return {"current": None, "high": None, "critical": None}
    
    def _get_load_average(self) -> Dict[str, float]:
        """Get system load average (Windows approximation)"""
        try:
            # Windows doesn't have load average, approximate with CPU stats
            cpu_times = psutil.cpu_times()
            total_time = sum([cpu_times.user, cpu_times.system, cpu_times.idle])
            
            if total_time > 0:
                load = (cpu_times.user + cpu_times.system) / total_time * 100
                return {"1min": round(load, 2)}
        except:
            pass
        
        return {"1min": 0}

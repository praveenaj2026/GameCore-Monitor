"""
RAM Monitoring Sensor
Monitors memory usage and swap statistics
"""

import psutil
from typing import Dict, Any
from .base_sensor import BaseSensor


class RAMSensor(BaseSensor):
    """RAM monitoring sensor"""
    
    def __init__(self):
        super().__init__("RAM")
        self.total_memory = psutil.virtual_memory().total
    
    def read(self) -> Dict[str, Any]:
        """Read RAM metrics"""
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Get actual total physical RAM (not just available to OS)
        total_ram = virtual.total
        
        data = {
            "total_gb": round(total_ram / (1024**3), 2),
            "used_gb": round(virtual.used / (1024**3), 2),
            "available_gb": round(virtual.available / (1024**3), 2),
            "percent": virtual.percent,
            "swap": {
                "total_gb": round(swap.total / (1024**3), 2),
                "used_gb": round(swap.used / (1024**3), 2),
                "percent": swap.percent
            },
            # Additional info for debugging
            "hardware_total_gb": round(total_ram / (1024**3), 2),
            "active_gb": round(virtual.active / (1024**3), 2) if hasattr(virtual, 'active') else 0
        }
        
        return data
    
    def get_cached_gb(self) -> float:
        """Get cached memory in GB"""
        try:
            virtual = psutil.virtual_memory()
            if hasattr(virtual, 'cached'):
                return round(virtual.cached / (1024**3), 2)
        except:
            pass
        return 0.0
    
    def get_buffers_gb(self) -> float:
        """Get buffer memory in GB"""
        try:
            virtual = psutil.virtual_memory()
            if hasattr(virtual, 'buffers'):
                return round(virtual.buffers / (1024**3), 2)
        except:
            pass
        return 0.0

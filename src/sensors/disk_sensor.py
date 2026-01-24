"""
Disk Monitoring Sensor
Monitors disk usage, I/O speeds, and health status
"""

import psutil
import time
from typing import Dict, Any, List
from .base_sensor import BaseSensor

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False


class DiskSensor(BaseSensor):
    """Disk monitoring sensor"""
    
    def __init__(self):
        super().__init__("Disk")
        self.last_disk_io = None
        self.last_io_time = None
        self.wmi_interface = None
        
        if WMI_AVAILABLE:
            try:
                self.wmi_interface = wmi.WMI()
            except:
                self.wmi_interface = None
    
    def read(self) -> Dict[str, Any]:
        """Read disk metrics"""
        data = {
            "partitions": self._get_partition_info(),
            "io_stats": self._get_io_stats(),
            "total_read_gb": 0,
            "total_write_gb": 0
        }
        
        # Calculate total I/O
        if data["io_stats"]:
            data["total_read_gb"] = round(
                sum(d.get("read_speed_mb", 0) for d in data["io_stats"].values()) / 1024, 2
            )
            data["total_write_gb"] = round(
                sum(d.get("write_speed_mb", 0) for d in data["io_stats"].values()) / 1024, 2
            )
        
        return data
    
    def _get_partition_info(self) -> List[Dict[str, Any]]:
        """Get partition/drive information"""
        partitions = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                part_info = {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent
                }
                
                partitions.append(part_info)
            except PermissionError:
                # Skip drives that can't be accessed
                continue
        
        return partitions
    
    def _get_io_stats(self) -> Dict[str, Dict[str, float]]:
        """Get disk I/O statistics with speed calculation"""
        io_stats = {}
        
        try:
            current_io = psutil.disk_io_counters(perdisk=True)
            current_time = time.time()
            
            if self.last_disk_io and self.last_io_time:
                time_delta = current_time - self.last_io_time
                
                for disk, counters in current_io.items():
                    if disk in self.last_disk_io:
                        last_counters = self.last_disk_io[disk]
                        
                        # Calculate speeds (bytes/sec -> MB/sec)
                        read_bytes = counters.read_bytes - last_counters.read_bytes
                        write_bytes = counters.write_bytes - last_counters.write_bytes
                        
                        read_speed = (read_bytes / time_delta) / (1024**2)
                        write_speed = (write_bytes / time_delta) / (1024**2)
                        
                        io_stats[disk] = {
                            "read_speed_mb": round(read_speed, 2),
                            "write_speed_mb": round(write_speed, 2),
                            "read_count": counters.read_count - last_counters.read_count,
                            "write_count": counters.write_count - last_counters.write_count,
                            "total_read_gb": round(counters.read_bytes / (1024**3), 2),
                            "total_write_gb": round(counters.write_bytes / (1024**3), 2)
                        }
            
            # Store for next calculation
            self.last_disk_io = current_io
            self.last_io_time = current_time
            
        except Exception as e:
            pass
        
        return io_stats
    
    def get_smart_status(self) -> Dict[str, str]:
        """Get SMART health status (requires WMI)"""
        smart_status = {}
        
        if not self.wmi_interface:
            return smart_status
        
        try:
            for disk in self.wmi_interface.Win32_DiskDrive():
                status = disk.Status
                smart_status[disk.Caption] = status if status else "Unknown"
        except:
            pass
        
        return smart_status

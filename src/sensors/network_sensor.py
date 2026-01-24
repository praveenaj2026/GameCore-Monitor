"""
Network Monitoring Sensor
Monitors network I/O speeds and statistics
"""

import psutil
import time
from typing import Dict, Any
from .base_sensor import BaseSensor


class NetworkSensor(BaseSensor):
    """Network monitoring sensor"""
    
    def __init__(self):
        super().__init__("Network")
        self.last_net_io = None
        self.last_io_time = None
    
    def read(self) -> Dict[str, Any]:
        """Read network metrics"""
        data = {
            "upload_speed_mbps": 0,
            "download_speed_mbps": 0,
            "total_sent_gb": 0,
            "total_recv_gb": 0,
            "connections": self._get_connection_count()
        }
        
        try:
            current_io = psutil.net_io_counters()
            current_time = time.time()
            
            # Calculate speeds
            if self.last_net_io and self.last_io_time:
                time_delta = current_time - self.last_io_time
                
                sent_bytes = current_io.bytes_sent - self.last_net_io.bytes_sent
                recv_bytes = current_io.bytes_recv - self.last_net_io.bytes_recv
                
                # Convert to Mbps
                upload_speed = (sent_bytes * 8 / time_delta) / (1024**2)
                download_speed = (recv_bytes * 8 / time_delta) / (1024**2)
                
                data["upload_speed_mbps"] = round(upload_speed, 2)
                data["download_speed_mbps"] = round(download_speed, 2)
            
            # Total data transferred
            data["total_sent_gb"] = round(current_io.bytes_sent / (1024**3), 2)
            data["total_recv_gb"] = round(current_io.bytes_recv / (1024**3), 2)
            
            # Store for next calculation
            self.last_net_io = current_io
            self.last_io_time = current_time
            
        except Exception as e:
            pass
        
        return data
    
    def _get_connection_count(self) -> Dict[str, int]:
        """Get count of network connections by status"""
        try:
            connections = psutil.net_connections()
            
            status_counts = {}
            for conn in connections:
                status = conn.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "total": len(connections),
                "established": status_counts.get("ESTABLISHED", 0),
                "listening": status_counts.get("LISTEN", 0),
                "other": sum(count for status, count in status_counts.items() 
                           if status not in ["ESTABLISHED", "LISTEN"])
            }
        except:
            return {"total": 0, "established": 0, "listening": 0, "other": 0}
    
    def get_interface_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get per-interface statistics"""
        try:
            return psutil.net_io_counters(pernic=True)
        except:
            return {}

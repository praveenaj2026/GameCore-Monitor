"""
System Monitoring Sensor
Monitors system-level information (uptime, boot time, processes)
"""

import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .base_sensor import BaseSensor


class SystemSensor(BaseSensor):
    """System-level monitoring sensor"""
    
    def __init__(self):
        super().__init__("System")
        self.boot_time = datetime.fromtimestamp(psutil.boot_time())
    
    def read(self) -> Dict[str, Any]:
        """Read system metrics"""
        data = {
            "uptime": self._get_uptime(),
            "boot_time": self.boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "processes": {
                "total": len(psutil.pids()),
                "running": len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'running']),
                "sleeping": len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'sleeping'])
            },
            "users": len(psutil.users())
        }
        
        return data
    
    def _get_uptime(self) -> Dict[str, Any]:
        """Get system uptime"""
        uptime_seconds = (datetime.now() - self.boot_time).total_seconds()
        uptime_delta = timedelta(seconds=uptime_seconds)
        
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            "seconds": int(uptime_seconds),
            "formatted": f"{days}d {hours}h {minutes}m",
            "days": days,
            "hours": hours,
            "minutes": minutes
        }
    
    def get_top_processes(self, count: int = 10, sort_by: str = "cpu") -> List[Dict[str, Any]]:
        """Get top resource-consuming processes"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                pinfo['cpu_percent'] = proc.cpu_percent(interval=0.1)
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by specified metric
        if sort_by == "cpu":
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        
        # Return top N
        top_processes = []
        for proc in processes[:count]:
            top_processes.append({
                "pid": proc.get('pid'),
                "name": proc.get('name'),
                "cpu_percent": round(proc.get('cpu_percent', 0), 1),
                "memory_percent": round(proc.get('memory_percent', 0), 1),
                "status": proc.get('status', 'unknown')
            })
        
        return top_processes
    
    def get_process_count_by_status(self) -> Dict[str, int]:
        """Get count of processes by status"""
        status_counts = {}
        
        for proc in psutil.process_iter(['status']):
            try:
                status = proc.info['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            except:
                continue
        
        return status_counts

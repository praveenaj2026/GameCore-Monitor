"""
GPU Monitoring Sensor
Monitors GPU usage, temperature, memory, and performance
"""

import psutil
from typing import Dict, Any, List, Optional
from .base_sensor import BaseSensor

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False


class GPUSensor(BaseSensor):
    """GPU monitoring sensor (primarily for NVIDIA cards)"""
    
    def __init__(self):
        super().__init__("GPU")
        self.has_nvidia = self._check_nvidia()
        self.wmi_interface = None
        
        if WMI_AVAILABLE:
            try:
                self.wmi_interface = wmi.WMI()
            except:
                self.wmi_interface = None
    
    def _check_nvidia(self) -> bool:
        """Check if NVIDIA GPU is available"""
        if not GPUTIL_AVAILABLE:
            return False
        
        try:
            gpus = GPUtil.getGPUs()
            return len(gpus) > 0
        except:
            return False
    
    def read(self) -> Dict[str, Any]:
        """Read GPU metrics"""
        if not self.has_nvidia:
            return {
                "available": False,
                "message": "No NVIDIA GPU detected or GPUtil not available"
            }
        
        data = {
            "available": True,
            "gpus": self._get_gpu_info()
        }
        
        return data
    
    def _get_gpu_info(self) -> List[Dict[str, Any]]:
        """Get information for all GPUs"""
        gpu_list = []
        
        try:
            gpus = GPUtil.getGPUs()
            
            for gpu in gpus:
                gpu_info = {
                    "id": gpu.id,
                    "name": gpu.name,
                    "load_percent": round(gpu.load * 100, 1),
                    "temperature_c": round(gpu.temperature, 1),
                    "memory": {
                        "total_mb": round(gpu.memoryTotal, 2),
                        "used_mb": round(gpu.memoryUsed, 2),
                        "free_mb": round(gpu.memoryFree, 2),
                        "percent": round((gpu.memoryUsed / gpu.memoryTotal) * 100, 1) if gpu.memoryTotal > 0 else 0
                    },
                    "driver": gpu.driver,
                    "uuid": gpu.uuid
                }
                
                gpu_list.append(gpu_info)
        except Exception as e:
            gpu_list = [{"error": str(e)}]
        
        return gpu_list
    
    def get_primary_gpu(self) -> Optional[Dict[str, Any]]:
        """Get primary/first GPU info"""
        data = self.read()
        if data.get("available") and data.get("gpus"):
            return data["gpus"][0]
        return None
    
    def get_max_temperature(self) -> float:
        """Get maximum temperature across all GPUs"""
        data = self.read()
        if not data.get("available"):
            return 0.0
        
        temps = [gpu.get("temperature_c", 0) for gpu in data.get("gpus", [])]
        return max(temps) if temps else 0.0
    
    def get_total_vram_usage(self) -> Dict[str, float]:
        """Get total VRAM usage across all GPUs"""
        data = self.read()
        if not data.get("available"):
            return {"total_mb": 0, "used_mb": 0, "free_mb": 0, "percent": 0}
        
        total_mb = 0
        used_mb = 0
        free_mb = 0
        
        for gpu in data.get("gpus", []):
            mem = gpu.get("memory", {})
            total_mb += mem.get("total_mb", 0)
            used_mb += mem.get("used_mb", 0)
            free_mb += mem.get("free_mb", 0)
        
        percent = (used_mb / total_mb * 100) if total_mb > 0 else 0
        
        return {
            "total_mb": round(total_mb, 2),
            "used_mb": round(used_mb, 2),
            "free_mb": round(free_mb, 2),
            "percent": round(percent, 1)
        }
    
    def get_fallback_info(self) -> List[Dict[str, Any]]:
        """Get basic GPU info from WMI (fallback if GPUtil fails)"""
        if not self.wmi_interface:
            return []
        
        gpu_list = []
        try:
            for gpu in self.wmi_interface.Win32_VideoController():
                gpu_info = {
                    "name": gpu.Name,
                    "adapter_ram_mb": round(int(gpu.AdapterRAM) / (1024**2), 2) if gpu.AdapterRAM else 0,
                    "driver_version": gpu.DriverVersion,
                    "status": gpu.Status
                }
                gpu_list.append(gpu_info)
        except:
            pass
        
        return gpu_list

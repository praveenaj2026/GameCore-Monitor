"""
Sensor Manager
Coordinates all hardware sensors and provides unified interface
"""

from typing import Dict, Any, Optional
from .cpu_sensor import CPUSensor
from .ram_sensor import RAMSensor
from .disk_sensor import DiskSensor
from .network_sensor import NetworkSensor
from .gpu_sensor import GPUSensor
from .system_sensor import SystemSensor


class SensorManager:
    """Manages all hardware sensors"""
    
    def __init__(self):
        self.cpu = CPUSensor()
        self.ram = RAMSensor()
        self.disk = DiskSensor()
        self.network = NetworkSensor()
        self.gpu = GPUSensor()
        self.system = SystemSensor()
        
        self.sensors = {
            "cpu": self.cpu,
            "ram": self.ram,
            "disk": self.disk,
            "network": self.network,
            "gpu": self.gpu,
            "system": self.system
        }
    
    def read_all(self) -> Dict[str, Any]:
        """Read all sensors"""
        data = {}
        
        for name, sensor in self.sensors.items():
            try:
                data[name] = sensor.update()
            except Exception as e:
                data[name] = {"error": str(e)}
        
        return data
    
    def read_sensor(self, sensor_name: str) -> Optional[Dict[str, Any]]:
        """Read specific sensor"""
        sensor = self.sensors.get(sensor_name)
        if sensor:
            return sensor.update()
        return None
    
    def enable_sensor(self, sensor_name: str):
        """Enable a sensor"""
        sensor = self.sensors.get(sensor_name)
        if sensor:
            sensor.enable()
    
    def disable_sensor(self, sensor_name: str):
        """Disable a sensor"""
        sensor = self.sensors.get(sensor_name)
        if sensor:
            sensor.disable()
    
    def get_sensor_status(self) -> Dict[str, bool]:
        """Get enabled status of all sensors"""
        return {name: sensor.enabled for name, sensor in self.sensors.items()}

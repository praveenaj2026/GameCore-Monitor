"""
Hardware Sensor Abstraction Layer
Base classes for all hardware monitoring sensors
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseSensor(ABC):
    """Abstract base class for all sensors"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.last_reading = None
        self.last_update = None
        
    @abstractmethod
    def read(self) -> Dict[str, Any]:
        """Read sensor data"""
        pass
    
    def update(self) -> Dict[str, Any]:
        """Update and return latest reading"""
        if not self.enabled:
            return {}
        
        try:
            self.last_reading = self.read()
            self.last_update = datetime.now()
            return self.last_reading
        except Exception as e:
            return {"error": str(e)}
    
    def get_last_reading(self) -> Optional[Dict[str, Any]]:
        """Get the last cached reading"""
        return self.last_reading
    
    def enable(self):
        """Enable the sensor"""
        self.enabled = True
    
    def disable(self):
        """Disable the sensor"""
        self.enabled = False


class SensorReading:
    """Container for sensor reading with metadata"""
    
    def __init__(self, sensor_name: str, data: Dict[str, Any], timestamp: datetime = None):
        self.sensor_name = sensor_name
        self.data = data
        self.timestamp = timestamp or datetime.now()
        
    def __repr__(self):
        return f"SensorReading({self.sensor_name}, {self.timestamp})"

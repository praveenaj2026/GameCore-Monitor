"""
Background Monitoring Thread
Continuously updates sensor data in background for instant dashboard access
Reduces load time from 2-3s to <500ms
"""

import threading
import time
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger("GameCore")


class BackgroundMonitor:
    """Background thread that continuously monitors hardware and caches results"""
    
    def __init__(self, sensor_manager, update_interval: float = 1.0):
        """
        Initialize background monitor
        
        Args:
            sensor_manager: SensorManager instance
            update_interval: Seconds between updates (default 1.0 for real-time)
        """
        self.sensor_manager = sensor_manager
        self.update_interval = update_interval
        
        # Cached data
        self.cached_data: Dict[str, Any] = {}
        self.last_update: datetime = None
        self.update_count: int = 0
        
        # Thread control
        self._running = False
        self._thread: threading.Thread = None
        self._lock = threading.Lock()
        
        # Performance metrics
        self.avg_update_time: float = 0.0
        self.max_update_time: float = 0.0
    
    def start(self):
        """Start background monitoring thread"""
        if self._running:
            logger.warning("Background monitor already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info(f"Background monitor started (interval: {self.update_interval}s)")
    
    def stop(self):
        """Stop background monitoring thread"""
        if not self._running:
            return
        
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("Background monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop - runs in background thread"""
        while self._running:
            try:
                start_time = time.time()
                
                # Update all sensors
                self.sensor_manager.update_all()
                
                # Cache all sensor data
                with self._lock:
                    self.cached_data = {
                        'cpu': self.sensor_manager.get_sensor("cpu").get_last_reading(),
                        'gpu': self.sensor_manager.get_sensor("gpu").get_last_reading(),
                        'ram': self.sensor_manager.get_sensor("ram").get_last_reading(),
                        'disk': self.sensor_manager.get_sensor("disk").get_last_reading(),
                        'network': self.sensor_manager.get_sensor("network").get_last_reading()
                    }
                    self.last_update = datetime.now()
                    self.update_count += 1
                
                # Track performance
                update_time = time.time() - start_time
                self.avg_update_time = (self.avg_update_time * (self.update_count - 1) + update_time) / self.update_count
                self.max_update_time = max(self.max_update_time, update_time)
                
                # Sleep until next update
                sleep_time = max(0, self.update_interval - update_time)
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Background monitor error: {e}")
                time.sleep(self.update_interval)
    
    def get_cached_data(self) -> Dict[str, Any]:
        """Get cached sensor data (instant access, no I/O wait)"""
        with self._lock:
            return self.cached_data.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        return {
            'running': self._running,
            'update_count': self.update_count,
            'last_update': self.last_update,
            'avg_update_time_ms': round(self.avg_update_time * 1000, 2),
            'max_update_time_ms': round(self.max_update_time * 1000, 2),
            'update_interval_s': self.update_interval
        }
    
    def is_healthy(self) -> bool:
        """Check if monitor is running and data is fresh"""
        if not self._running:
            return False
        
        if not self.last_update:
            return False
        
        # Data should be less than 5 seconds old
        age = (datetime.now() - self.last_update).total_seconds()
        return age < 5.0

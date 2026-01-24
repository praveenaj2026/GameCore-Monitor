"""
Alert System
Monitors metrics and triggers alerts based on thresholds
"""

import time
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert:
    """Represents a single alert"""
    
    def __init__(self, 
                 name: str, 
                 level: AlertLevel, 
                 message: str, 
                 value: Any = None,
                 threshold: Any = None):
        self.name = name
        self.level = level
        self.message = message
        self.value = value
        self.threshold = threshold
        self.timestamp = datetime.now()
        self.acknowledged = False
    
    def __repr__(self):
        return f"Alert({self.level.value}: {self.name})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "level": self.level.value,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "acknowledged": self.acknowledged
        }


class AlertRule:
    """Defines an alert rule with condition checking"""
    
    def __init__(self,
                 name: str,
                 condition: Callable[[Any], bool],
                 level: AlertLevel,
                 message_template: str,
                 duration: int = 0,
                 cooldown: int = 300):
        self.name = name
        self.condition = condition
        self.level = level
        self.message_template = message_template
        self.duration = duration  # seconds condition must be true
        self.cooldown = cooldown  # seconds between alerts
        
        self.condition_start_time = None
        self.last_alert_time = None
    
    def check(self, value: Any) -> Optional[Alert]:
        """Check if condition triggers alert"""
        current_time = time.time()
        
        # Check if condition is met
        if self.condition(value):
            # Start timing if not already
            if self.condition_start_time is None:
                self.condition_start_time = current_time
            
            # Check if duration requirement met
            if current_time - self.condition_start_time >= self.duration:
                # Check cooldown
                if self.last_alert_time is None or \
                   current_time - self.last_alert_time >= self.cooldown:
                    
                    # Trigger alert
                    message = self.message_template.format(value=value)
                    alert = Alert(
                        name=self.name,
                        level=self.level,
                        message=message,
                        value=value
                    )
                    
                    self.last_alert_time = current_time
                    return alert
        else:
            # Reset timing if condition not met
            self.condition_start_time = None
        
        return None
    
    def reset(self):
        """Reset rule state"""
        self.condition_start_time = None
        self.last_alert_time = None


class AlertManager:
    """Manages alert rules and active alerts"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self.max_history = 100
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.rules[rule.name] = rule
    
    def remove_rule(self, rule_name: str):
        """Remove an alert rule"""
        if rule_name in self.rules:
            del self.rules[rule_name]
    
    def check_rules(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check all rules against current metrics"""
        new_alerts = []
        
        for rule_name, rule in self.rules.items():
            # Extract value for this rule (using nested dict paths)
            value = self._extract_value(metrics, rule_name)
            
            if value is not None:
                alert = rule.check(value)
                if alert:
                    new_alerts.append(alert)
                    self.active_alerts.append(alert)
                    self.alert_history.append(alert)
        
        # Trim history
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        return new_alerts
    
    def _extract_value(self, metrics: Dict[str, Any], path: str) -> Any:
        """Extract value from nested dict using dot notation"""
        # Simple extraction (e.g., "cpu.usage_percent")
        keys = path.split('.')
        value = metrics
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by level"""
        if level:
            return [a for a in self.active_alerts if a.level == level]
        return self.active_alerts
    
    def acknowledge_alert(self, alert: Alert):
        """Acknowledge an alert"""
        alert.acknowledged = True
    
    def clear_acknowledged(self):
        """Clear acknowledged alerts"""
        self.active_alerts = [a for a in self.active_alerts if not a.acknowledged]
    
    def clear_all(self):
        """Clear all active alerts"""
        self.active_alerts.clear()
    
    def reset_all_rules(self):
        """Reset all rule states"""
        for rule in self.rules.values():
            rule.reset()


def create_default_rules() -> List[AlertRule]:
    """Create default alert rules"""
    rules = [
        # CPU usage alert
        AlertRule(
            name="cpu.usage_percent",
            condition=lambda x: x > 90,
            level=AlertLevel.WARNING,
            message_template="CPU usage high: {value:.1f}%",
            duration=120,  # 2 minutes
            cooldown=300
        ),
        
        # GPU temperature alert
        AlertRule(
            name="gpu.gpus.0.temperature_c",
            condition=lambda x: x > 85,
            level=AlertLevel.CRITICAL,
            message_template="GPU temperature critical: {value:.1f}°C",
            duration=0,
            cooldown=300
        ),
        
        # RAM usage alert
        AlertRule(
            name="ram.percent",
            condition=lambda x: x > 90,
            level=AlertLevel.WARNING,
            message_template="RAM usage high: {value:.1f}%",
            duration=60,
            cooldown=300
        ),
    ]
    
    return rules

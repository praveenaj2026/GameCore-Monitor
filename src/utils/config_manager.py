"""
Configuration Manager
Handles loading and managing configuration settings
"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.default_config_path = os.path.join(config_dir, "default_config.json")
        self.user_config_path = os.path.join(config_dir, "user_settings.json")
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration (default + user overrides)"""
        # Load default config
        config = {}
        if os.path.exists(self.default_config_path):
            with open(self.default_config_path, 'r') as f:
                config = json.load(f)
        
        # Load user config (overrides)
        if os.path.exists(self.user_config_path):
            with open(self.user_config_path, 'r') as f:
                user_config = json.load(f)
                config = self._merge_configs(config, user_config)
        
        return config
    
    def _merge_configs(self, default: Dict, override: Dict) -> Dict:
        """Merge user config into default config"""
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_user_config(self):
        """Save current config as user config"""
        os.makedirs(self.config_dir, exist_ok=True)
        
        with open(self.user_config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def reset_to_default(self):
        """Reset to default configuration"""
        if os.path.exists(self.default_config_path):
            with open(self.default_config_path, 'r') as f:
                self.config = json.load(f)

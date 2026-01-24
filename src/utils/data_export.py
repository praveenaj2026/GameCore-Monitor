"""
Data Export Utilities
Export monitoring data to CSV, JSON, and other formats
"""

import csv
import json
from typing import Dict, Any, List
from datetime import datetime
import os


class DataExporter:
    """Handles exporting monitoring data"""
    
    def __init__(self, export_dir: str = "data/exports"):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """Export data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gamecore_export_{timestamp}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        if not data:
            return filepath
        
        # Get all unique keys
        keys = set()
        for row in data:
            keys.update(self._flatten_dict(row).keys())
        
        keys = sorted(keys)
        
        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            
            for row in data:
                flat_row = self._flatten_dict(row)
                writer.writerow(flat_row)
        
        return filepath
    
    def export_to_json(self, data: Any, filename: str = None) -> str:
        """Export data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gamecore_export_{timestamp}.json"
        
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filepath
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def create_snapshot(self, metrics: Dict[str, Any]) -> str:
        """Create a snapshot of current metrics"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{timestamp}.json"
        
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        return self.export_to_json(snapshot, filename)

"""Storage system for servitors"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from .servitor import Servitor, ServitorStatus


class Storage:
    """Manages servitor data storage"""
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize storage system"""
        if base_path is None:
            # Get the servitor package directory
            base_path = Path(__file__).parent.parent
        
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data"
        self.servitors_path = self.data_path / "servitors"
        self.sigils_path = self.data_path / "sigils"
        self.metadata_path = self.data_path / "metadata.json"
        
        # Create directories if they don't exist
        self.servitors_path.mkdir(parents=True, exist_ok=True)
        self.sigils_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata if it doesn't exist
        if not self.metadata_path.exists():
            self._save_metadata({})
    
    def _get_servitor_filename(self, name: str) -> str:
        """Get filename for a servitor"""
        # Sanitize name for filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        return f"{safe_name}.json"
    
    def _save_metadata(self, metadata: Dict):
        """Save metadata file"""
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_metadata(self) -> Dict:
        """Load metadata file"""
        if not self.metadata_path.exists():
            return {}
        try:
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def save_servitor(self, servitor: Servitor) -> bool:
        """Save a servitor to disk"""
        try:
            filename = self._get_servitor_filename(servitor.name)
            filepath = self.servitors_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(servitor.to_dict(), f, indent=2)
            
            # Update metadata
            metadata = self._load_metadata()
            metadata[servitor.name] = {
                "filename": filename,
                "status": servitor.status.value,
                "charge_level": servitor.charge_level,
                "creation_date": servitor.creation_date.isoformat(),
            }
            self._save_metadata(metadata)
            
            return True
        except Exception as e:
            print(f"Error saving servitor: {e}")
            return False
    
    def load_servitor(self, name: str, apply_decay: bool = True) -> Optional[Servitor]:
        """Load a servitor by name"""
        try:
            metadata = self._load_metadata()
            if name not in metadata:
                return None
            
            filename = metadata[name]["filename"]
            filepath = self.servitors_path / filename
            
            if not filepath.exists():
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            servitor = Servitor.from_dict(data)
            
            # Apply energy decay when loading
            if apply_decay:
                from .maintenance import MaintenanceManager
                MaintenanceManager.apply_energy_decay(servitor)
                # Save if decay was applied
                if servitor.last_charged:
                    days_passed = (datetime.now() - servitor.last_charged).total_seconds() / 86400
                    if days_passed > 0:
                        self.save_servitor(servitor)
            
            return servitor
        except Exception as e:
            print(f"Error loading servitor: {e}")
            return None
    
    def list_servitors(self, status_filter: Optional[str] = None) -> List[str]:
        """List all servitor names, optionally filtered by status"""
        metadata = self._load_metadata()
        
        if status_filter:
            return [
                name for name, info in metadata.items()
                if info.get("status") == status_filter
            ]
        
        return list(metadata.keys())
    
    def delete_servitor(self, name: str) -> bool:
        """Delete a servitor"""
        try:
            metadata = self._load_metadata()
            if name not in metadata:
                return False
            
            filename = metadata[name]["filename"]
            filepath = self.servitors_path / filename
            
            if filepath.exists():
                filepath.unlink()
            
            # Remove from metadata
            del metadata[name]
            self._save_metadata(metadata)
            
            return True
        except Exception as e:
            print(f"Error deleting servitor: {e}")
            return False
    
    def archive_servitor(self, servitor: Servitor) -> bool:
        """Archive a dismissed servitor"""
        servitor.status = ServitorStatus.DISMISSED
        return self.save_servitor(servitor)
    
    def get_all_servitors(self) -> List[Servitor]:
        """Load all servitors"""
        servitors = []
        for name in self.list_servitors():
            servitor = self.load_servitor(name)
            if servitor:
                servitors.append(servitor)
        return servitors


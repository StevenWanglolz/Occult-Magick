"""Maintenance and feeding routines for servitors"""

from datetime import datetime, timedelta
from typing import List, Dict
from .servitor import Servitor, ServitorStatus


class MaintenanceManager:
    """Manages maintenance and feeding for servitors"""
    
    # Energy decay rate per day (percentage points)
    DEFAULT_DECAY_RATE = 1.0
    
    # Feeding reminder threshold (days since last fed)
    FEEDING_REMINDER_DAYS = 7
    
    @staticmethod
    def calculate_energy_decay(
        servitor: Servitor,
        decay_rate: float = None
    ) -> float:
        """
        Calculate energy decay since last charge
        
        Args:
            servitor: Servitor to calculate decay for
            decay_rate: Decay rate per day (default: DEFAULT_DECAY_RATE)
        
        Returns:
            Amount of charge lost
        """
        if decay_rate is None:
            decay_rate = MaintenanceManager.DEFAULT_DECAY_RATE
        
        if not servitor.last_charged:
            return 0.0
        
        days_passed = (datetime.now() - servitor.last_charged).total_seconds() / 86400
        decay_amount = days_passed * decay_rate
        
        return min(decay_amount, servitor.charge_level)
    
    @staticmethod
    def apply_energy_decay(servitor: Servitor, decay_rate: float = None):
        """
        Apply energy decay to servitor
        
        Args:
            servitor: Servitor to apply decay to
            decay_rate: Decay rate per day
        """
        decay_amount = MaintenanceManager.calculate_energy_decay(servitor, decay_rate)
        
        if decay_amount > 0:
            servitor.charge_level = max(0.0, servitor.charge_level - decay_amount)
            
            # If charge drops below activation threshold, deactivate
            if servitor.charge_level < servitor.activation_threshold:
                servitor.deactivate()
    
    @staticmethod
    def feed_servitor(servitor: Servitor, amount: float = 10.0):
        """
        Feed a servitor (recharge energy)
        
        Args:
            servitor: Servitor to feed
            amount: Amount of charge to add
        """
        servitor.feed(amount)
    
    @staticmethod
    def check_health(servitor: Servitor) -> Dict[str, any]:
        """
        Check servitor health status
        
        Returns:
            Dictionary with health information
        """
        health_info = {
            "charge_level": servitor.charge_level,
            "status": servitor.status.value,
            "days_since_fed": None,
            "days_since_charged": None,
            "needs_feeding": False,
            "needs_charging": False,
            "is_healthy": True,
        }
        
        if servitor.last_fed:
            days_fed = (datetime.now() - servitor.last_fed).total_seconds() / 86400
            health_info["days_since_fed"] = days_fed
            health_info["needs_feeding"] = days_fed >= MaintenanceManager.FEEDING_REMINDER_DAYS
        
        if servitor.last_charged:
            days_charged = (datetime.now() - servitor.last_charged).total_seconds() / 86400
            health_info["days_since_charged"] = days_charged
        
        # Check if charge is low
        if servitor.charge_level < servitor.activation_threshold:
            health_info["needs_charging"] = True
            health_info["is_healthy"] = False
        
        # Check if servitor is dismissed
        if servitor.status == ServitorStatus.DISMISSED:
            health_info["is_healthy"] = False
        
        return health_info
    
    @staticmethod
    def get_maintenance_reminders(servitors: List[Servitor]) -> List[Dict]:
        """
        Get maintenance reminders for all servitors
        
        Args:
            servitors: List of servitors to check
        
        Returns:
            List of maintenance reminders
        """
        reminders = []
        
        for servitor in servitors:
            if servitor.status == ServitorStatus.DISMISSED:
                continue
            
            health = MaintenanceManager.check_health(servitor)
            
            if health["needs_feeding"]:
                reminders.append({
                    "servitor": servitor.name,
                    "type": "feeding",
                    "message": f"{servitor.name} needs feeding (last fed {health['days_since_fed']:.1f} days ago)",
                    "priority": "medium"
                })
            
            if health["needs_charging"]:
                reminders.append({
                    "servitor": servitor.name,
                    "type": "charging",
                    "message": f"{servitor.name} needs charging (charge level: {servitor.charge_level:.1f}%)",
                    "priority": "high"
                })
        
        return reminders
    
    @staticmethod
    def perform_maintenance(servitor: Servitor, auto_feed: bool = False):
        """
        Perform maintenance on a servitor
        
        Args:
            servitor: Servitor to maintain
            auto_feed: If True, automatically feed if needed
        """
        # Apply energy decay
        MaintenanceManager.apply_energy_decay(servitor)
        
        # Auto-feed if enabled and needed
        if auto_feed:
            health = MaintenanceManager.check_health(servitor)
            if health["needs_feeding"]:
                MaintenanceManager.feed_servitor(servitor)


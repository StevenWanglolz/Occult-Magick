"""Maintenance and feeding routines for servitors"""

from datetime import datetime, timedelta
from typing import List, Dict
from .servitor import Servitor, ServitorStatus


class MaintenanceManager:
    """Manages maintenance and feeding for servitors"""

    # Energy decay rates per day (percentage points)
    ACTIVE_DECAY_RATE = 5.0
    DORMANT_DECAY_RATE = 1.0
    DEFAULT_DECAY_RATE = 1.0

    # Cost of evocative manifestation (opening/loading servitor)
    EVOCATION_COST = 0.1
    EVOCATION_COOLDOWN_MINUTES = 10

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
            from .servitor import ServitorStatus
            decay_rate = MaintenanceManager.ACTIVE_DECAY_RATE if servitor.status == ServitorStatus.ACTIVE else MaintenanceManager.DORMANT_DECAY_RATE

        # Use last_maintenance_check if available, otherwise fallback to last_charged
        reference_time = servitor.last_maintenance_check or servitor.last_charged
        
        if not reference_time:
            return 0.0

        days_passed = (datetime.now() - reference_time).total_seconds() / 86400
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
        decay_amount = MaintenanceManager.calculate_energy_decay(
            servitor, decay_rate)

        if decay_amount > 0:
            servitor.charge_level = max(
                0.0, servitor.charge_level - decay_amount)
            
            # Update the check timestamp to prevent cumulative decay on next load
            servitor.last_maintenance_check = datetime.now()

            # If charge drops below activation threshold, deactivate
            if servitor.charge_level < servitor.activation_threshold:
                servitor.deactivate()
        else:
            # Even if no decay (e.g. < 1 second passed), update the check time 
            # if it was never set to ensure we have a baseline.
            if not servitor.last_maintenance_check:
                servitor.last_maintenance_check = datetime.now()

    @staticmethod
    def apply_evocation_cost(servitor: Servitor):
        """
        Apply energy cost for evoking a servitor, respecting cooldown.

        Args:
            servitor: Servitor to apply cost to
        """
        if servitor.status != ServitorStatus.DISMISSED:
            # Check for cooldown
            now = datetime.now()
            if servitor.last_evocation:
                time_since_last = (
                    now - servitor.last_evocation).total_seconds() / 60
                if time_since_last < MaintenanceManager.EVOCATION_COOLDOWN_MINUTES:
                    return  # Still in cooldown

            # Apply cost
            servitor.charge_level = max(
                0.0, servitor.charge_level - MaintenanceManager.EVOCATION_COST)
            servitor.last_evocation = now

            # Re-check activation status
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
        # No automatic performance boost - you decide when to boost performance

    @staticmethod
    def check_health(servitor: Servitor) -> Dict[str, any]:
        """
        Check servitor health status

        Returns:
            Dictionary with health information
        """
        health_info = {
            "charge_level": servitor.charge_level,
            "performance_level": servitor.performance_level,
            "status": servitor.status.value,
            "days_since_fed": None,
            "days_since_charged": None,
            "days_since_performance_boost": None,
            "needs_feeding": False,
            "needs_charging": False,
            "is_healthy": True,
        }

        if servitor.last_fed:
            days_fed = (datetime.now() -
                        servitor.last_fed).total_seconds() / 86400
            health_info["days_since_fed"] = days_fed
            health_info["needs_feeding"] = days_fed >= MaintenanceManager.FEEDING_REMINDER_DAYS

        if servitor.last_charged:
            days_charged = (datetime.now() -
                            servitor.last_charged).total_seconds() / 86400
            health_info["days_since_charged"] = days_charged

        if servitor.last_performance_boost:
            days_boost = (
                datetime.now() - servitor.last_performance_boost).total_seconds() / 86400
            health_info["days_since_performance_boost"] = days_boost

        # Check if charge is low
        if servitor.charge_level < servitor.activation_threshold:
            health_info["needs_charging"] = True
            health_info["is_healthy"] = False

        # Performance is informational only - you decide when to boost
        # (removed automatic "needs boost" warning - manual control)

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

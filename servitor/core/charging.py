"""Charging mechanisms for servitors"""

import time
import threading
from datetime import datetime
from typing import Callable, Optional
from .servitor import Servitor


class ChargingSession:
    """Manages a charging session for a servitor"""
    
    def __init__(self, servitor: Servitor, method: str = "visualization"):
        """
        Initialize charging session
        
        Args:
            servitor: The servitor to charge
            method: Charging method ("visualization", "repetition", "ritual")
        """
        self.servitor = servitor
        self.method = method
        self.is_active = False
        self.thread: Optional[threading.Thread] = None
        self.charge_rate = 0.1  # Charge per second
        self.update_callback: Optional[Callable] = None
    
    def set_update_callback(self, callback: Callable):
        """Set callback function for charge updates"""
        self.update_callback = callback
    
    def _repetition_charging(self):
        """Repetition-based charging (like Intention Repeater)"""
        intention = f"{self.servitor.name} {self.servitor.purpose}"
        iteration = 0
        
        while self.is_active:
            # Repeat intention millions of times per second (simulated)
            for _ in range(1000000):
                if not self.is_active:
                    break
                _ = intention  # Simulate repetition
            
            iteration += 1
            
            # Add charge periodically
            if iteration % 10 == 0:
                self.servitor.add_charge(self.charge_rate, method=self.method)
                if self.update_callback:
                    self.update_callback(self.servitor.charge_level)
            
            time.sleep(0.01)  # Small delay to prevent CPU overload
    
    def _visualization_charging(self):
        """Visualization-based charging"""
        while self.is_active:
            self.servitor.add_charge(self.charge_rate, method=self.method)
            if self.update_callback:
                self.update_callback(self.servitor.charge_level)
            time.sleep(1.0)  # Charge every second
    
    def _ritual_charging(self):
        """Ritual-based charging (slower, more deliberate)"""
        while self.is_active:
            # Ritual charging is slower but more powerful
            self.servitor.add_charge(self.charge_rate * 2, method=self.method)
            if self.update_callback:
                self.update_callback(self.servitor.charge_level)
            time.sleep(2.0)  # Charge every 2 seconds
    
    def start(self, duration: Optional[float] = None):
        """
        Start charging session
        
        Args:
            duration: Duration in seconds (None for indefinite)
        """
        if self.is_active:
            return
        
        self.is_active = True
        
        # Select charging method
        if self.method == "repetition":
            target = self._repetition_charging
        elif self.method == "ritual":
            target = self._ritual_charging
        else:
            target = self._visualization_charging
        
        def charging_thread():
            if duration:
                end_time = time.time() + duration
                while self.is_active and time.time() < end_time:
                    target()
            else:
                while self.is_active:
                    target()
        
        self.thread = threading.Thread(target=charging_thread, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop charging session"""
        self.is_active = False
        if self.thread:
            self.thread.join(timeout=1.0)


class ChargingManager:
    """Manages charging operations for servitors"""
    
    @staticmethod
    def charge_servitor(
        servitor: Servitor,
        amount: float,
        method: str = "manual"
    ):
        """
        Add charge to servitor
        
        Args:
            servitor: Servitor to charge
            amount: Amount of charge to add (0-100)
            method: Charging method
        """
        servitor.add_charge(amount, method=method)
    
    @staticmethod
    def start_charging_session(
        servitor: Servitor,
        method: str = "visualization",
        duration: Optional[float] = None,
        update_callback: Optional[Callable] = None
    ) -> ChargingSession:
        """
        Start a charging session
        
        Args:
            servitor: Servitor to charge
            method: Charging method ("visualization", "repetition", "ritual")
            duration: Duration in seconds (None for indefinite)
            update_callback: Callback function for charge updates
        
        Returns:
            ChargingSession object
        """
        session = ChargingSession(servitor, method=method)
        if update_callback:
            session.set_update_callback(update_callback)
        session.start(duration=duration)
        return session
    
    @staticmethod
    def can_activate(servitor: Servitor) -> bool:
        """Check if servitor can be activated"""
        return servitor.can_activate()
    
    @staticmethod
    def activate(servitor: Servitor) -> bool:
        """Activate servitor if conditions are met"""
        return servitor.activate()


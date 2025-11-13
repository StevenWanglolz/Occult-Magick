"""Servitor data model"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class ServitorStatus(Enum):
    """Servitor status states"""
    DORMANT = "dormant"
    ACTIVE = "active"
    DISMISSED = "dismissed"


@dataclass
class Task:
    """Represents a task for a servitor"""
    name: str
    description: str
    task_type: str  # e.g., "file_operation", "reminder", "data_processing"
    parameters: Dict = field(default_factory=dict)
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0
    auto_execute: bool = False  # Auto-execute when servitor is active
    execution_interval_hours: float = 24.0  # Hours between auto-executions


@dataclass
class Servitor:
    """Represents a chaos magick servitor"""
    name: str
    purpose: str
    sigil_path: Optional[str] = None
    charge_level: float = 0.0  # 0-100
    performance_level: float = 50.0  # 0-100, affects task success rates
    status: ServitorStatus = ServitorStatus.DORMANT
    creation_date: datetime = field(default_factory=datetime.now)
    last_fed: Optional[datetime] = None
    last_charged: Optional[datetime] = None
    last_performance_boost: Optional[datetime] = None
    activation_threshold: float = 50.0  # Minimum charge to activate
    tasks: List[Task] = field(default_factory=list)
    charging_history: List[Dict] = field(default_factory=list)
    performance_history: List[Dict] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict:
        """Convert servitor to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "purpose": self.purpose,
            "sigil_path": self.sigil_path,
            "charge_level": self.charge_level,
            "performance_level": self.performance_level,
            "status": self.status.value,
            "creation_date": self.creation_date.isoformat(),
            "last_fed": self.last_fed.isoformat() if self.last_fed else None,
            "last_charged": self.last_charged.isoformat() if self.last_charged else None,
            "last_performance_boost": self.last_performance_boost.isoformat() if self.last_performance_boost else None,
            "activation_threshold": self.activation_threshold,
            "performance_history": self.performance_history,
            "tasks": [
                {
                    "name": task.name,
                    "description": task.description,
                    "task_type": task.task_type,
                    "parameters": task.parameters,
                    "last_executed": task.last_executed.isoformat() if task.last_executed else None,
                    "execution_count": task.execution_count,
                    "success_count": task.success_count,
                    "auto_execute": task.auto_execute,
                    "execution_interval_hours": task.execution_interval_hours,
                }
                for task in self.tasks
            ],
            "charging_history": self.charging_history,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Servitor":
        """Create servitor from dictionary"""
        servitor = cls(
            name=data["name"],
            purpose=data["purpose"],
            sigil_path=data.get("sigil_path"),
            charge_level=data.get("charge_level", 0.0),
            performance_level=data.get("performance_level", 50.0),
            status=ServitorStatus(data.get("status", "dormant")),
            creation_date=datetime.fromisoformat(data["creation_date"]) if isinstance(data.get("creation_date"), str) else data.get("creation_date", datetime.now()),
            last_fed=datetime.fromisoformat(data["last_fed"]) if data.get("last_fed") else None,
            last_charged=datetime.fromisoformat(data["last_charged"]) if data.get("last_charged") else None,
            last_performance_boost=datetime.fromisoformat(data["last_performance_boost"]) if data.get("last_performance_boost") else None,
            activation_threshold=data.get("activation_threshold", 50.0),
            notes=data.get("notes", ""),
        )
        
        servitor.performance_history = data.get("performance_history", [])
        
        # Load tasks
        for task_data in data.get("tasks", []):
            task = Task(
                name=task_data["name"],
                description=task_data["description"],
                task_type=task_data["task_type"],
                parameters=task_data.get("parameters", {}),
                last_executed=datetime.fromisoformat(task_data["last_executed"]) if task_data.get("last_executed") else None,
                execution_count=task_data.get("execution_count", 0),
                success_count=task_data.get("success_count", 0),
                auto_execute=task_data.get("auto_execute", False),
                execution_interval_hours=task_data.get("execution_interval_hours", 24.0),
            )
            servitor.tasks.append(task)
        
        servitor.charging_history = data.get("charging_history", [])
        return servitor
    
    def can_activate(self) -> bool:
        """Check if servitor has enough charge to activate"""
        return self.charge_level >= self.activation_threshold and self.status != ServitorStatus.DISMISSED
    
    def activate(self) -> bool:
        """Activate the servitor if conditions are met"""
        if self.can_activate():
            self.status = ServitorStatus.ACTIVE
            # Check for auto-execute tasks when activating
            self._check_auto_execute_tasks()
            return True
        return False
    
    def _check_auto_execute_tasks(self):
        """Check and execute tasks that are due for auto-execution"""
        if self.status != ServitorStatus.ACTIVE:
            return
        
        from .tasks import TaskExecutor
        executor = TaskExecutor(self)
        
        for task in self.tasks:
            if not task.auto_execute:
                continue
            
            # Check if task is due for execution
            if task.last_executed:
                hours_since = (datetime.now() - task.last_executed).total_seconds() / 3600
                if hours_since < task.execution_interval_hours:
                    continue
            # If never executed, execute now
            
            # Execute the task
            executor.execute_task(task)
    
    def deactivate(self):
        """Deactivate the servitor"""
        if self.status != ServitorStatus.DISMISSED:
            self.status = ServitorStatus.DORMANT
    
    def add_charge(self, amount: float, method: str = "manual"):
        """Add charge to the servitor"""
        self.charge_level = min(100.0, self.charge_level + amount)
        self.last_charged = datetime.now()
        self.charging_history.append({
            "timestamp": datetime.now().isoformat(),
            "amount": amount,
            "method": method,
            "new_level": self.charge_level,
        })
    
    def feed(self, amount: float = 10.0):
        """Feed the servitor (recharge energy)"""
        self.add_charge(amount, method="feeding")
        self.last_fed = datetime.now()
    
    def boost_performance(self, amount: float = 10.0, reason: str = "charging"):
        """
        Boost servitor performance (affects task success rates)
        
        Args:
            amount: Performance boost amount (0-100)
            reason: Reason for the boost (e.g., "charging", "ritual", "feeding")
        """
        old_performance = self.performance_level
        self.performance_level = min(100.0, self.performance_level + amount)
        self.last_performance_boost = datetime.now()
        
        self.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "amount": amount,
            "reason": reason,
            "old_level": old_performance,
            "new_level": self.performance_level,
        })
    
    def get_performance_modifier(self) -> float:
        """
        Get performance modifier for task success (0.0 to 2.0)
        - 0% performance = 0.5x modifier (50% base success)
        - 50% performance = 1.0x modifier (normal success)
        - 100% performance = 2.0x modifier (double success chance)
        """
        # Linear scaling: 0% -> 0.5x, 50% -> 1.0x, 100% -> 2.0x
        return 0.5 + (self.performance_level / 100.0) * 1.5


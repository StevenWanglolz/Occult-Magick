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


@dataclass
class Servitor:
    """Represents a chaos magick servitor"""
    name: str
    purpose: str
    sigil_path: Optional[str] = None
    charge_level: float = 0.0  # 0-100
    status: ServitorStatus = ServitorStatus.DORMANT
    creation_date: datetime = field(default_factory=datetime.now)
    last_fed: Optional[datetime] = None
    last_charged: Optional[datetime] = None
    activation_threshold: float = 50.0  # Minimum charge to activate
    tasks: List[Task] = field(default_factory=list)
    charging_history: List[Dict] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict:
        """Convert servitor to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "purpose": self.purpose,
            "sigil_path": self.sigil_path,
            "charge_level": self.charge_level,
            "status": self.status.value,
            "creation_date": self.creation_date.isoformat(),
            "last_fed": self.last_fed.isoformat() if self.last_fed else None,
            "last_charged": self.last_charged.isoformat() if self.last_charged else None,
            "activation_threshold": self.activation_threshold,
            "tasks": [
                {
                    "name": task.name,
                    "description": task.description,
                    "task_type": task.task_type,
                    "parameters": task.parameters,
                    "last_executed": task.last_executed.isoformat() if task.last_executed else None,
                    "execution_count": task.execution_count,
                    "success_count": task.success_count,
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
            status=ServitorStatus(data.get("status", "dormant")),
            creation_date=datetime.fromisoformat(data["creation_date"]) if isinstance(data.get("creation_date"), str) else data.get("creation_date", datetime.now()),
            last_fed=datetime.fromisoformat(data["last_fed"]) if data.get("last_fed") else None,
            last_charged=datetime.fromisoformat(data["last_charged"]) if data.get("last_charged") else None,
            activation_threshold=data.get("activation_threshold", 50.0),
            notes=data.get("notes", ""),
        )
        
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
            return True
        return False
    
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


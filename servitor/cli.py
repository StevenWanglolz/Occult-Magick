"""Command-line interface for servitor management"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Handle both package and direct execution
if __name__ == '__main__':
    # Add Magick directory (parent of servitor) to path for direct execution
    servitor_dir = os.path.dirname(os.path.abspath(__file__))
    magick_dir = os.path.dirname(servitor_dir)
    if magick_dir not in sys.path:
        sys.path.insert(0, magick_dir)
    from servitor.core.storage import Storage
    from servitor.core.servitor import Servitor, Task
    from servitor.core.sigil import SigilGenerator
    from servitor.core.charging import ChargingManager
    from servitor.core.tasks import TaskExecutor
    from servitor.core.maintenance import MaintenanceManager
    from servitor.core.dismissal import DismissalProtocol
else:
    from .core.storage import Storage
    from .core.servitor import Servitor, Task
    from .core.sigil import SigilGenerator
    from .core.charging import ChargingManager
    from .core.tasks import TaskExecutor
    from .core.maintenance import MaintenanceManager
    from .core.dismissal import DismissalProtocol


class ServitorCLI:
    """Command-line interface for servitor operations"""
    
    def __init__(self):
        """Initialize CLI"""
        self.storage = Storage()
        self.sigil_generator = SigilGenerator()
    
    def create_servitor(
        self,
        name: str,
        purpose: str,
        sigil_type: str = "witch_wheel",
        initial_charge: float = 0.0
    ):
        """Create a new servitor"""
        # Check if servitor already exists
        if self.storage.load_servitor(name):
            print(f"Error: Servitor '{name}' already exists")
            return False
        
        # Generate sigil
        sigil_path = self.storage.sigils_path / f"{name}_sigil.png"
        try:
            self.sigil_generator.generate_from_servitor(
                name,
                purpose,
                position_type=sigil_type,
                output_dir=self.storage.sigils_path
            )
        except Exception as e:
            print(f"Warning: Could not generate sigil: {e}")
            sigil_path = None
        
        # Create servitor
        servitor = Servitor(
            name=name,
            purpose=purpose,
            sigil_path=str(sigil_path) if sigil_path else None,
            charge_level=initial_charge
        )
        
        # Save servitor
        if self.storage.save_servitor(servitor):
            print(f"Servitor '{name}' created successfully!")
            print(f"  Purpose: {purpose}")
            print(f"  Sigil: {sigil_path}")
            print(f"  Initial Charge: {initial_charge}%")
            return True
        else:
            print(f"Error: Failed to save servitor '{name}'")
            return False
    
    def list_servitors(self, status_filter: Optional[str] = None):
        """List all servitors"""
        servitors = self.storage.get_all_servitors()
        
        if status_filter:
            servitors = [s for s in servitors if s.status.value == status_filter]
        
        if not servitors:
            print("No servitors found.")
            return
        
        print(f"\n{'Name':<20} {'Status':<12} {'Charge':<10} {'Purpose':<40}")
        print("-" * 85)
        
        for servitor in servitors:
            print(
                f"{servitor.name:<20} "
                f"{servitor.status.value:<12} "
                f"{servitor.charge_level:>6.1f}%   "
                f"{servitor.purpose[:37]:<40}"
            )
    
    def show_servitor(self, name: str):
        """Show detailed information about a servitor"""
        servitor = self.storage.load_servitor(name)
        
        if not servitor:
            print(f"Error: Servitor '{name}' not found")
            return
        
        print(f"\n=== {servitor.name} ===")
        print(f"Purpose: {servitor.purpose}")
        print(f"Status: {servitor.status.value}")
        print(f"Charge Level: {servitor.charge_level:.1f}%")
        print(f"Activation Threshold: {servitor.activation_threshold:.1f}%")
        print(f"Created: {servitor.creation_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if servitor.last_fed:
            print(f"Last Fed: {servitor.last_fed.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if servitor.last_charged:
            print(f"Last Charged: {servitor.last_charged.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if servitor.sigil_path:
            print(f"Sigil: {servitor.sigil_path}")
        
        if servitor.tasks:
            print(f"\nTasks ({len(servitor.tasks)}):")
            for task in servitor.tasks:
                print(f"  - {task.name}: {task.description}")
                print(f"    Type: {task.task_type}, Executions: {task.execution_count}")
        
        if servitor.notes:
            print(f"\nNotes:\n{servitor.notes}")
    
    def charge_servitor(self, name: str, amount: float, method: str = "manual"):
        """Charge a servitor"""
        servitor = self.storage.load_servitor(name)
        
        if not servitor:
            print(f"Error: Servitor '{name}' not found")
            return False
        
        ChargingManager.charge_servitor(servitor, amount, method=method)
        self.storage.save_servitor(servitor)
        
        print(f"Charged {servitor.name} by {amount}% (new level: {servitor.charge_level:.1f}%)")
        return True
    
    def activate_servitor(self, name: str):
        """Activate a servitor"""
        servitor = self.storage.load_servitor(name)
        
        if not servitor:
            print(f"Error: Servitor '{name}' not found")
            return False
        
        if ChargingManager.activate(servitor):
            self.storage.save_servitor(servitor)
            print(f"Servitor '{name}' activated!")
            return True
        else:
            print(f"Error: Cannot activate '{name}' (charge level: {servitor.charge_level:.1f}%, threshold: {servitor.activation_threshold:.1f}%)")
            return False
    
    def feed_servitor(self, name: str, amount: float = 10.0):
        """Feed a servitor"""
        servitor = self.storage.load_servitor(name)
        
        if not servitor:
            print(f"Error: Servitor '{name}' not found")
            return False
        
        MaintenanceManager.feed_servitor(servitor, amount)
        self.storage.save_servitor(servitor)
        
        print(f"Fed {servitor.name} (+{amount}% charge, new level: {servitor.charge_level:.1f}%)")
        return True
    
    def execute_task(self, servitor_name: str, task_name: Optional[str] = None):
        """Execute tasks for a servitor"""
        servitor = self.storage.load_servitor(servitor_name)
        
        if not servitor:
            print(f"Error: Servitor '{servitor_name}' not found")
            return False
        
        executor = TaskExecutor(servitor)
        
        if task_name:
            result = executor.execute_task_by_name(task_name)
            if result:
                print(f"Task '{task_name}' executed: {result}")
            else:
                print(f"Error: Task '{task_name}' not found")
        else:
            results = executor.execute_all_tasks()
            print(f"Executed {len(results)} tasks for {servitor_name}")
            for result in results:
                print(f"  - {result.get('task', 'unknown')}: {result.get('success', False)}")
        
        self.storage.save_servitor(servitor)
        return True
    
    def add_task(
        self,
        servitor_name: str,
        task_name: str,
        description: str,
        task_type: str,
        parameters: dict = None
    ):
        """Add a task to a servitor"""
        servitor = self.storage.load_servitor(servitor_name)
        
        if not servitor:
            print(f"Error: Servitor '{servitor_name}' not found")
            return False
        
        task = Task(
            name=task_name,
            description=description,
            task_type=task_type,
            parameters=parameters or {}
        )
        
        servitor.tasks.append(task)
        self.storage.save_servitor(servitor)
        
        print(f"Task '{task_name}' added to {servitor_name}")
        return True
    
    def check_health(self, name: Optional[str] = None):
        """Check servitor health"""
        if name:
            servitor = self.storage.load_servitor(name)
            if not servitor:
                print(f"Error: Servitor '{name}' not found")
                return False
            
            health = MaintenanceManager.check_health(servitor)
            print(f"\n=== Health Check: {servitor.name} ===")
            print(f"Charge Level: {health['charge_level']:.1f}%")
            print(f"Status: {health['status']}")
            print(f"Healthy: {health['is_healthy']}")
            
            if health['days_since_fed']:
                print(f"Days since fed: {health['days_since_fed']:.1f}")
            if health['days_since_charged']:
                print(f"Days since charged: {health['days_since_charged']:.1f}")
            
            if health['needs_feeding']:
                print("⚠️  Needs feeding!")
            if health['needs_charging']:
                print("⚠️  Needs charging!")
        else:
            servitors = self.storage.get_all_servitors()
            reminders = MaintenanceManager.get_maintenance_reminders(servitors)
            
            if reminders:
                print("\n=== Maintenance Reminders ===")
                for reminder in reminders:
                    print(f"[{reminder['priority'].upper()}] {reminder['message']}")
            else:
                print("All servitors are healthy!")
    
    def dismiss_servitor(self, name: str, reason: str = ""):
        """Dismiss a servitor"""
        servitor = self.storage.load_servitor(name)
        
        if not servitor:
            print(f"Error: Servitor '{name}' not found")
            return False
        
        protocol = DismissalProtocol(self.storage)
        return protocol.perform_dismissal_ritual(servitor)
    
    def run(self):
        """Run the CLI"""
        parser = argparse.ArgumentParser(description="Digital Chaos Magick Servitor Manager")
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Create servitor
        create_parser = subparsers.add_parser('create', help='Create a new servitor')
        create_parser.add_argument('name', help='Servitor name')
        create_parser.add_argument('purpose', help='Servitor purpose/intention')
        create_parser.add_argument('--sigil-type', choices=['witch_wheel', 'random'], default='witch_wheel')
        create_parser.add_argument('--initial-charge', type=float, default=0.0)
        
        # List servitors
        list_parser = subparsers.add_parser('list', help='List all servitors')
        list_parser.add_argument('--status', choices=['dormant', 'active', 'dismissed'])
        
        # Show servitor
        show_parser = subparsers.add_parser('show', help='Show servitor details')
        show_parser.add_argument('name', help='Servitor name')
        
        # Charge servitor
        charge_parser = subparsers.add_parser('charge', help='Charge a servitor')
        charge_parser.add_argument('name', help='Servitor name')
        charge_parser.add_argument('amount', type=float, help='Charge amount')
        charge_parser.add_argument('--method', default='manual')
        
        # Activate servitor
        activate_parser = subparsers.add_parser('activate', help='Activate a servitor')
        activate_parser.add_argument('name', help='Servitor name')
        
        # Feed servitor
        feed_parser = subparsers.add_parser('feed', help='Feed a servitor')
        feed_parser.add_argument('name', help='Servitor name')
        feed_parser.add_argument('--amount', type=float, default=10.0)
        
        # Execute task
        exec_parser = subparsers.add_parser('execute', help='Execute servitor tasks')
        exec_parser.add_argument('servitor', help='Servitor name')
        exec_parser.add_argument('--task', help='Specific task name (optional)')
        
        # Add task
        add_task_parser = subparsers.add_parser('add-task', help='Add a task to a servitor')
        add_task_parser.add_argument('servitor', help='Servitor name')
        add_task_parser.add_argument('task_name', help='Task name')
        add_task_parser.add_argument('description', help='Task description')
        add_task_parser.add_argument('task_type', choices=['file_operation', 'reminder', 'data_processing', 'log'])
        
        # Health check
        health_parser = subparsers.add_parser('health', help='Check servitor health')
        health_parser.add_argument('name', nargs='?', help='Servitor name (optional, checks all if omitted)')
        
        # Dismiss servitor
        dismiss_parser = subparsers.add_parser('dismiss', help='Dismiss a servitor')
        dismiss_parser.add_argument('name', help='Servitor name')
        dismiss_parser.add_argument('--reason', default='', help='Reason for dismissal')
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # Execute command
        if args.command == 'create':
            self.create_servitor(args.name, args.purpose, args.sigil_type, args.initial_charge)
        elif args.command == 'list':
            self.list_servitors(args.status)
        elif args.command == 'show':
            self.show_servitor(args.name)
        elif args.command == 'charge':
            self.charge_servitor(args.name, args.amount, args.method)
        elif args.command == 'activate':
            self.activate_servitor(args.name)
        elif args.command == 'feed':
            self.feed_servitor(args.name, args.amount)
        elif args.command == 'execute':
            self.execute_task(args.servitor, args.task)
        elif args.command == 'add-task':
            self.add_task(args.servitor, args.task_name, args.description, args.task_type)
        elif args.command == 'health':
            self.check_health(args.name)
        elif args.command == 'dismiss':
            self.dismiss_servitor(args.name, args.reason)


def main():
    """Main entry point for CLI"""
    cli = ServitorCLI()
    cli.run()


if __name__ == '__main__':
    main()


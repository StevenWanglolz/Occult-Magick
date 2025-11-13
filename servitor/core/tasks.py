"""Task execution engine for servitors"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from .servitor import Servitor, Task


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executes tasks for servitors"""
    
    def __init__(self, servitor: Servitor):
        """Initialize task executor for a servitor"""
        self.servitor = servitor
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a task
        
        Args:
            task: Task to execute
        
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Executing task '{task.name}' for servitor '{self.servitor.name}' (Performance: {self.servitor.performance_level:.1f}%)")
        
        try:
            result = self._execute_by_type(task)
            task.execution_count += 1
            task.last_executed = datetime.now()
            
            # Apply performance modifier to success chance
            performance_modifier = self.servitor.get_performance_modifier()
            import random
            base_success = result.get("success", False)
            
            # If base success, apply performance modifier
            if base_success:
                # Higher performance = more likely to succeed
                success_chance = min(1.0, performance_modifier / 2.0)
                if random.random() < success_chance:
                    task.success_count += 1
                    result["performance_boosted"] = True
                    result["performance_level"] = self.servitor.performance_level
                else:
                    result["success"] = False
                    result["performance_boosted"] = False
                    result["note"] = "Task execution affected by low performance"
            else:
                # Even failed tasks might succeed with high performance
                if performance_modifier > 1.5:
                    retry_chance = (performance_modifier - 1.0) / 2.0
                    if random.random() < retry_chance:
                        result["success"] = True
                        task.success_count += 1
                        result["performance_saved"] = True
                        result["performance_level"] = self.servitor.performance_level
            
            # Performance doesn't decay automatically - you recharge when you feel it needs a boost
            # (removed automatic decay - manual control only)
            
            return result
        except Exception as e:
            logger.error(f"Error executing task '{task.name}': {e}")
            task.execution_count += 1
            task.last_executed = datetime.now()
            return {
                "success": False,
                "error": str(e),
                "task": task.name
            }
    
    def _execute_by_type(self, task: Task) -> Dict[str, Any]:
        """Execute task based on its type"""
        task_type = task.task_type.lower()
        
        if task_type == "file_operation":
            return self._execute_file_operation(task)
        elif task_type == "reminder":
            return self._execute_reminder(task)
        elif task_type == "data_processing":
            return self._execute_data_processing(task)
        elif task_type == "log":
            return self._execute_log(task)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    def _execute_file_operation(self, task: Task) -> Dict[str, Any]:
        """Execute file operation task"""
        params = task.parameters
        operation = params.get("operation", "create")
        file_path = params.get("file_path")
        content = params.get("content", "")
        
        if not file_path:
            return {"success": False, "error": "No file_path specified"}
        
        path = Path(file_path)
        
        try:
            if operation == "create":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
                return {"success": True, "message": f"File created: {file_path}"}
            
            elif operation == "append":
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'a') as f:
                    f.write(content)
                return {"success": True, "message": f"Content appended to: {file_path}"}
            
            elif operation == "delete":
                if path.exists():
                    path.unlink()
                    return {"success": True, "message": f"File deleted: {file_path}"}
                else:
                    return {"success": False, "error": f"File not found: {file_path}"}
            
            elif operation == "read":
                if path.exists():
                    content = path.read_text()
                    return {"success": True, "content": content, "file_path": file_path}
                else:
                    return {"success": False, "error": f"File not found: {file_path}"}
            
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_reminder(self, task: Task) -> Dict[str, Any]:
        """Execute reminder task"""
        params = task.parameters
        message = params.get("message", f"Reminder from {self.servitor.name}")
        
        logger.info(f"REMINDER: {message}")
        print(f"\n🔔 REMINDER: {message}\n")
        
        return {
            "success": True,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_data_processing(self, task: Task) -> Dict[str, Any]:
        """Execute data processing task"""
        params = task.parameters
        operation = params.get("operation", "count")
        data = params.get("data", "")
        
        try:
            if operation == "count":
                count = len(data.split()) if isinstance(data, str) else len(data)
                return {"success": True, "result": count, "operation": "count"}
            
            elif operation == "transform":
                transform_type = params.get("transform_type", "upper")
                if transform_type == "upper":
                    result = data.upper() if isinstance(data, str) else str(data).upper()
                elif transform_type == "lower":
                    result = data.lower() if isinstance(data, str) else str(data).lower()
                else:
                    result = data
                return {"success": True, "result": result, "operation": "transform"}
            
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_log(self, task: Task) -> Dict[str, Any]:
        """Execute logging task"""
        params = task.parameters
        message = params.get("message", f"Log entry from {self.servitor.name}")
        log_file = params.get("log_file")
        
        log_entry = f"[{datetime.now().isoformat()}] {self.servitor.name}: {message}\n"
        
        if log_file:
            try:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(log_path, 'a') as f:
                    f.write(log_entry)
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        logger.info(message)
        return {"success": True, "message": message}
    
    def execute_all_tasks(self) -> List[Dict[str, Any]]:
        """Execute all tasks for the servitor"""
        results = []
        for task in self.servitor.tasks:
            result = self.execute_task(task)
            results.append(result)
        return results
    
    def execute_task_by_name(self, task_name: str) -> Optional[Dict[str, Any]]:
        """Execute a specific task by name"""
        for task in self.servitor.tasks:
            if task.name == task_name:
                return self.execute_task(task)
        return None


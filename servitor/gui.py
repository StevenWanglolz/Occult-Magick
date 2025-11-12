"""GUI interface for servitor management"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from PIL import Image, ImageTk
import threading
import sys
import os

# Handle both package and direct execution
if __name__ == '__main__':
    # Add Magick directory (parent of servitor) to path for direct execution
    servitor_dir = os.path.dirname(os.path.abspath(__file__))
    magick_dir = os.path.dirname(servitor_dir)
    if magick_dir not in sys.path:
        sys.path.insert(0, magick_dir)
    from servitor.core.storage import Storage
    from servitor.core.servitor import Servitor, Task, ServitorStatus
    from servitor.core.sigil import SigilGenerator
    from servitor.core.charging import ChargingManager, ChargingSession
    from servitor.core.tasks import TaskExecutor
    from servitor.core.maintenance import MaintenanceManager
    from servitor.core.dismissal import DismissalProtocol
else:
    from .core.storage import Storage
    from .core.servitor import Servitor, Task, ServitorStatus
    from .core.sigil import SigilGenerator
    from .core.charging import ChargingManager, ChargingSession
    from .core.tasks import TaskExecutor
    from .core.maintenance import MaintenanceManager
    from .core.dismissal import DismissalProtocol


class ServitorGUI:
    """Graphical user interface for servitor management"""
    
    MSG_SELECT_SERVITOR = "Please select a servitor"
    
    def __init__(self, root):
        """Initialize GUI"""
        self.root = root
        self.root.title("Digital Chaos Magick Servitor Manager")
        self.root.geometry("900x700")
        
        self.storage = Storage()
        self.sigil_generator = SigilGenerator()
        self.current_servitor = None
        self.charging_session = None
        
        self.create_widgets()
        self.refresh_servitor_list()
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left panel - Servitor list
        left_frame = ttk.LabelFrame(main_frame, text="Servitors", padding="5")
        left_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Servitor listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.servitor_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.servitor_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.servitor_listbox.bind('<<ListboxSelect>>', self.on_servitor_select)
        scrollbar.config(command=self.servitor_listbox.yview)
        
        # Buttons for servitor management
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="Create New", command=self.create_servitor_dialog).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_servitor_list).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_servitor).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Right panel - Servitor details
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Details tab
        self.details_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.details_frame, text="Details")
        self.create_details_tab()
        
        # Charging tab
        self.charging_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.charging_frame, text="Charging")
        self.create_charging_tab()
        
        # Tasks tab
        self.tasks_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tasks_frame, text="Tasks")
        self.create_tasks_tab()
        
        # Health tab
        self.health_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.health_frame, text="Health")
        self.create_health_tab()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def create_details_tab(self):
        """Create details tab"""
        # Servitor info
        info_frame = ttk.LabelFrame(self.details_frame, text="Servitor Information", padding="5")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.name_label = ttk.Label(info_frame, text="", font=("Arial", 12, "bold"))
        self.name_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Purpose:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.purpose_label = ttk.Label(info_frame, text="", wraplength=400)
        self.purpose_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Status:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.status_label = ttk.Label(info_frame, text="")
        self.status_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Charge Level:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.charge_label = ttk.Label(info_frame, text="", font=("Arial", 10))
        self.charge_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Charge progress bar
        self.charge_progress = ttk.Progressbar(info_frame, length=300, mode='determinate')
        self.charge_progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Sigil display
        sigil_frame = ttk.LabelFrame(self.details_frame, text="Sigil", padding="5")
        sigil_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.sigil_label = ttk.Label(sigil_frame, text="No sigil loaded")
        self.sigil_label.pack(expand=True)
        
        # Action buttons
        action_frame = ttk.Frame(self.details_frame)
        action_frame.pack(pady=5)
        
        self.edit_btn = ttk.Button(action_frame, text="Edit Servitor", command=self.edit_servitor_dialog)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.activate_btn = ttk.Button(action_frame, text="Activate Servitor", command=self.activate_current_servitor)
        self.activate_btn.pack(side=tk.LEFT, padx=5)
    
    def create_charging_tab(self):
        """Create charging tab"""
        # Charging method selection
        method_frame = ttk.LabelFrame(self.charging_frame, text="Charging Method", padding="5")
        method_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.charging_method = tk.StringVar(value="visualization")
        ttk.Radiobutton(method_frame, text="Visualization", variable=self.charging_method, value="visualization").pack(anchor=tk.W)
        ttk.Radiobutton(method_frame, text="Repetition", variable=self.charging_method, value="repetition").pack(anchor=tk.W)
        ttk.Radiobutton(method_frame, text="Ritual", variable=self.charging_method, value="ritual").pack(anchor=tk.W)
        
        # Manual charge
        manual_frame = ttk.LabelFrame(self.charging_frame, text="Manual Charge", padding="5")
        manual_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(manual_frame, text="Amount:").pack(side=tk.LEFT, padx=5)
        self.charge_amount_var = tk.StringVar(value="10.0")
        ttk.Entry(manual_frame, textvariable=self.charge_amount_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(manual_frame, text="Add Charge", command=self.manual_charge).pack(side=tk.LEFT, padx=5)
        
        # Charging session controls
        session_frame = ttk.LabelFrame(self.charging_frame, text="Charging Session", padding="5")
        session_frame.pack(fill=tk.X)
        
        self.start_charge_btn = ttk.Button(session_frame, text="Start Charging", command=self.start_charging)
        self.start_charge_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_charge_btn = ttk.Button(session_frame, text="Stop Charging", command=self.stop_charging, state=tk.DISABLED)
        self.stop_charge_btn.pack(side=tk.LEFT, padx=5)
        
        # Charge level display
        self.charge_display_label = ttk.Label(self.charging_frame, text="Charge Level: 0.0%", font=("Arial", 14))
        self.charge_display_label.pack(pady=10)
    
    def create_tasks_tab(self):
        """Create tasks tab"""
        # Task list
        list_frame = ttk.LabelFrame(self.tasks_frame, text="Tasks", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Task listbox
        task_scrollbar = ttk.Scrollbar(list_frame)
        task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_listbox = tk.Listbox(list_frame, yscrollcommand=task_scrollbar.set)
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        task_scrollbar.config(command=self.task_listbox.yview)
        
        # Task buttons
        task_btn_frame = ttk.Frame(self.tasks_frame)
        task_btn_frame.pack(fill=tk.X)
        
        ttk.Button(task_btn_frame, text="Add Task", command=self.add_task_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(task_btn_frame, text="Execute Selected", command=self.execute_selected_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(task_btn_frame, text="Execute All", command=self.execute_all_tasks).pack(side=tk.LEFT, padx=2)
    
    def create_health_tab(self):
        """Create health tab"""
        self.health_text = tk.Text(self.health_frame, wrap=tk.WORD, height=20)
        self.health_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(self.health_frame, text="Refresh Health Check", command=self.update_health_display).pack(pady=5)
    
    def refresh_servitor_list(self, preserve_selection=True):
        """Refresh the servitor list"""
        # Preserve current selection if any
        selected_name = None
        if preserve_selection and self.current_servitor:
            selected_name = self.current_servitor.name
        
        self.servitor_listbox.delete(0, tk.END)
        servitors = self.storage.get_all_servitors()
        selected_index = None
        for i, servitor in enumerate(servitors):
            status_icon = "●" if servitor.status == ServitorStatus.ACTIVE else "○"
            self.servitor_listbox.insert(tk.END, f"{status_icon} {servitor.name} ({servitor.charge_level:.1f}%)")
            if preserve_selection and selected_name and servitor.name == selected_name:
                selected_index = i
        
        # Restore selection if it existed
        if preserve_selection and selected_index is not None:
            self.servitor_listbox.selection_set(selected_index)
            self.servitor_listbox.see(selected_index)
    
    def on_servitor_select(self, event):
        """Handle servitor selection"""
        selection = self.servitor_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        servitors = self.storage.get_all_servitors()
        if index < len(servitors):
            self.current_servitor = servitors[index]
            self.update_servitor_display()
    
    def update_servitor_display(self):
        """Update display with current servitor info"""
        if not self.current_servitor:
            return
        
        servitor = self.current_servitor
        
        # Update labels
        self.name_label.config(text=servitor.name)
        self.purpose_label.config(text=servitor.purpose)
        self.status_label.config(text=servitor.status.value)
        self.charge_label.config(text=f"{servitor.charge_level:.1f}%")
        self.charge_progress['value'] = servitor.charge_level
        self.charge_display_label.config(text=f"Charge Level: {servitor.charge_level:.1f}%")
        
        # Update sigil
        if servitor.sigil_path and Path(servitor.sigil_path).exists():
            try:
                img = Image.open(servitor.sigil_path)
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.sigil_label.config(image=photo, text="")
                self.sigil_label.image = photo  # Keep a reference
            except Exception as e:
                self.sigil_label.config(text=f"Error loading sigil: {e}")
        else:
            self.sigil_label.config(text="No sigil available", image="")
        
        # Update tasks
        self.task_listbox.delete(0, tk.END)
        for task in servitor.tasks:
            self.task_listbox.insert(tk.END, f"{task.name}: {task.description}")
        
        # Update buttons
        if servitor.status == ServitorStatus.DISMISSED:
            self.edit_btn.config(state=tk.DISABLED)
            self.activate_btn.config(state=tk.DISABLED)
        else:
            self.edit_btn.config(state=tk.NORMAL)
            if servitor.can_activate():
                self.activate_btn.config(state=tk.NORMAL)
            else:
                self.activate_btn.config(state=tk.DISABLED)
        
        # Update health
        self.update_health_display()
    
    def create_servitor_dialog(self):
        """Create servitor creation dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Servitor")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Purpose/Intention:").pack(pady=5)
        purpose_text = tk.Text(dialog, width=40, height=5)
        purpose_text.pack(pady=5)
        
        ttk.Label(dialog, text="Sigil Type:").pack(pady=5)
        sigil_type_var = tk.StringVar(value="witch_wheel")
        ttk.Radiobutton(dialog, text="Witch Wheel", variable=sigil_type_var, value="witch_wheel").pack()
        ttk.Radiobutton(dialog, text="Random", variable=sigil_type_var, value="random").pack()
        
        def create():
            name = name_entry.get().strip()
            purpose = purpose_text.get("1.0", tk.END).strip()
            
            if not name or not purpose:
                messagebox.showerror("Error", "Name and purpose are required")
                return
            
            # Generate sigil
            sigil_path = self.storage.sigils_path / f"{name}_sigil.png"
            try:
                self.sigil_generator.generate_from_servitor(
                    name, purpose,
                    position_type=sigil_type_var.get(),
                    output_dir=self.storage.sigils_path
                )
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not generate sigil: {e}")
                sigil_path = None
            
            # Create servitor
            servitor = Servitor(
                name=name,
                purpose=purpose,
                sigil_path=str(sigil_path) if sigil_path else None
            )
            
            if self.storage.save_servitor(servitor):
                messagebox.showinfo("Success", f"Servitor '{name}' created successfully!")
                self.refresh_servitor_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create servitor")
        
        ttk.Button(dialog, text="Create", command=create).pack(pady=10)
    
    def edit_servitor_dialog(self):
        """Edit servitor properties dialog"""
        if not self.current_servitor:
            messagebox.showwarning("Warning", self.MSG_SELECT_SERVITOR)
            return
        
        if self.current_servitor.status == ServitorStatus.DISMISSED:
            messagebox.showwarning("Warning", "Cannot edit dismissed servitors")
            return
        
        servitor = self.current_servitor
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Servitor: {servitor.name}")
        dialog.geometry("450x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Name (read-only, can't change name as it's used as key)
        ttk.Label(dialog, text="Name:").pack(pady=5)
        name_label = ttk.Label(dialog, text=servitor.name, font=("Arial", 10, "bold"))
        name_label.pack(pady=5)
        ttk.Label(dialog, text="(Name cannot be changed)", font=("Arial", 8), foreground="gray").pack()
        
        # Purpose
        ttk.Label(dialog, text="Purpose/Intention:").pack(pady=(10, 5))
        purpose_text = tk.Text(dialog, width=50, height=5)
        purpose_text.insert("1.0", servitor.purpose)
        purpose_text.pack(pady=5)
        
        # Activation threshold
        ttk.Label(dialog, text="Activation Threshold (%):").pack(pady=(10, 5))
        threshold_var = tk.StringVar(value=str(servitor.activation_threshold))
        threshold_entry = ttk.Entry(dialog, textvariable=threshold_var, width=10)
        threshold_entry.pack(pady=5)
        
        # Notes
        ttk.Label(dialog, text="Notes:").pack(pady=(10, 5))
        notes_text = tk.Text(dialog, width=50, height=6)
        notes_text.insert("1.0", servitor.notes)
        notes_text.pack(pady=5)
        
        # Regenerate sigil option
        regenerate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="Regenerate sigil", variable=regenerate_var).pack(pady=5)
        
        def save():
            purpose = purpose_text.get("1.0", tk.END).strip()
            notes = notes_text.get("1.0", tk.END).strip()
            
            if not purpose:
                messagebox.showerror("Error", "Purpose is required")
                return
            
            try:
                threshold = float(threshold_var.get())
                if threshold < 0 or threshold > 100:
                    raise ValueError("Threshold must be between 0 and 100")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid threshold: {e}")
                return
            
            # Update servitor
            servitor.purpose = purpose
            servitor.activation_threshold = threshold
            servitor.notes = notes
            
            # Regenerate sigil if requested
            if regenerate_var.get():
                sigil_path = self.storage.sigils_path / f"{servitor.name}_sigil.png"
                try:
                    self.sigil_generator.generate_from_servitor(
                        servitor.name, servitor.purpose,
                        position_type="witch_wheel",  # Default to witch wheel
                        output_dir=self.storage.sigils_path
                    )
                    servitor.sigil_path = str(sigil_path)
                except Exception as e:
                    messagebox.showwarning("Warning", f"Could not regenerate sigil: {e}")
            
            # Save servitor
            if self.storage.save_servitor(servitor):
                messagebox.showinfo("Success", f"Servitor '{servitor.name}' updated successfully!")
                self.refresh_servitor_list()
                self.update_servitor_display()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update servitor")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Save", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_servitor(self):
        """Delete selected servitor"""
        selection = self.servitor_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a servitor to delete")
            return
        
        index = selection[0]
        servitors = self.storage.get_all_servitors()
        if index >= len(servitors):
            return
        
        servitor = servitors[index]
        
        if messagebox.askyesno("Confirm", f"Delete servitor '{servitor.name}'?"):
            if self.storage.delete_servitor(servitor.name):
                messagebox.showinfo("Success", "Servitor deleted")
                self.current_servitor = None
                self.refresh_servitor_list()
                self.update_servitor_display()
            else:
                messagebox.showerror("Error", "Failed to delete servitor")
    
    def manual_charge(self):
        """Manually charge current servitor"""
        if not self.current_servitor:
            messagebox.showwarning("Warning", self.MSG_SELECT_SERVITOR)
            return
        
        try:
            amount = float(self.charge_amount_var.get())
            ChargingManager.charge_servitor(self.current_servitor, amount)
            self.storage.save_servitor(self.current_servitor)
            self.update_servitor_display()
            self.refresh_servitor_list()  # Update the list to show new charge percentage
        except ValueError:
            messagebox.showerror("Error", "Invalid charge amount")
    
    def start_charging(self):
        """Start charging session"""
        if not self.current_servitor:
            messagebox.showwarning("Warning", self.MSG_SELECT_SERVITOR)
            return
        
        method = self.charging_method.get()
        
        def update_callback(charge_level):
            self.root.after(0, lambda: self.charge_display_label.config(text=f"Charge Level: {charge_level:.1f}%"))
            self.root.after(0, lambda: self.update_servitor_display())
            self.root.after(0, lambda: self.refresh_servitor_list())  # Update the list to show new charge percentage
        
        self.charging_session = ChargingManager.start_charging_session(
            self.current_servitor,
            method=method,
            update_callback=update_callback
        )
        
        self.start_charge_btn.config(state=tk.DISABLED)
        self.stop_charge_btn.config(state=tk.NORMAL)
    
    def stop_charging(self):
        """Stop charging session"""
        if self.charging_session:
            self.charging_session.stop()
            self.charging_session = None
            self.storage.save_servitor(self.current_servitor)
            self.start_charge_btn.config(state=tk.NORMAL)
            self.stop_charge_btn.config(state=tk.DISABLED)
            self.update_servitor_display()
            self.refresh_servitor_list()  # Update the list to show final charge percentage
    
    def activate_current_servitor(self):
        """Activate current servitor"""
        if not self.current_servitor:
            return
        
        if ChargingManager.activate(self.current_servitor):
            self.storage.save_servitor(self.current_servitor)
            messagebox.showinfo("Success", f"Servitor '{self.current_servitor.name}' activated!")
            self.refresh_servitor_list()
            self.update_servitor_display()
        else:
            messagebox.showerror("Error", "Cannot activate servitor (insufficient charge)")
    
    def add_task_dialog(self):
        """Add task dialog"""
        if not self.current_servitor:
            messagebox.showwarning("Warning", self.MSG_SELECT_SERVITOR)
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Task")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Task Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Description:").pack(pady=5)
        desc_text = tk.Text(dialog, width=40, height=3)
        desc_text.pack(pady=5)
        
        ttk.Label(dialog, text="Task Type:").pack(pady=5)
        type_var = tk.StringVar(value="reminder")
        ttk.Radiobutton(dialog, text="Reminder", variable=type_var, value="reminder").pack()
        ttk.Radiobutton(dialog, text="File Operation", variable=type_var, value="file_operation").pack()
        ttk.Radiobutton(dialog, text="Data Processing", variable=type_var, value="data_processing").pack()
        ttk.Radiobutton(dialog, text="Log", variable=type_var, value="log").pack()
        
        def add():
            name = name_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            task_type = type_var.get()
            
            if not name:
                messagebox.showerror("Error", "Task name is required")
                return
            
            task = Task(name=name, description=description, task_type=task_type)
            self.current_servitor.tasks.append(task)
            self.storage.save_servitor(self.current_servitor)
            self.update_servitor_display()
            dialog.destroy()
        
        ttk.Button(dialog, text="Add", command=add).pack(pady=10)
    
    def execute_selected_task(self):
        """Execute selected task"""
        if not self.current_servitor:
            return
        
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        index = selection[0]
        if index < len(self.current_servitor.tasks):
            task = self.current_servitor.tasks[index]
            executor = TaskExecutor(self.current_servitor)
            result = executor.execute_task(task)
            self.storage.save_servitor(self.current_servitor)
            messagebox.showinfo("Task Executed", f"Task '{task.name}': {result.get('success', False)}")
            self.update_servitor_display()
    
    def execute_all_tasks(self):
        """Execute all tasks"""
        if not self.current_servitor:
            return
        
        executor = TaskExecutor(self.current_servitor)
        results = executor.execute_all_tasks()
        self.storage.save_servitor(self.current_servitor)
        
        success_count = sum(1 for r in results if r.get('success', False))
        messagebox.showinfo("Tasks Executed", f"Executed {len(results)} tasks, {success_count} successful")
        self.update_servitor_display()
    
    def update_health_display(self):
        """Update health display"""
        if not self.current_servitor:
            self.health_text.delete("1.0", tk.END)
            return
        
        servitor = self.current_servitor
        health = MaintenanceManager.check_health(servitor)
        
        text = f"=== Health Check: {servitor.name} ===\n\n"
        text += f"Charge Level: {health['charge_level']:.1f}%\n"
        text += f"Status: {health['status']}\n"
        text += f"Healthy: {health['is_healthy']}\n\n"
        
        if health['days_since_fed']:
            text += f"Days since fed: {health['days_since_fed']:.1f}\n"
        if health['days_since_charged']:
            text += f"Days since charged: {health['days_since_charged']:.1f}\n"
        
        text += "\n"
        
        if health['needs_feeding']:
            text += "⚠️  Needs feeding!\n"
        if health['needs_charging']:
            text += "⚠️  Needs charging!\n"
        
        # Check all servitors
        text += "\n=== All Servitors Maintenance ===\n\n"
        all_servitors = self.storage.get_all_servitors()
        reminders = MaintenanceManager.get_maintenance_reminders(all_servitors)
        
        if reminders:
            for reminder in reminders:
                text += f"[{reminder['priority'].upper()}] {reminder['message']}\n"
        else:
            text += "All servitors are healthy!\n"
        
        self.health_text.delete("1.0", tk.END)
        self.health_text.insert("1.0", text)


def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    ServitorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()


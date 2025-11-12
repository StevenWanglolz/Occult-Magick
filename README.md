# Digital Chaos Magick Servitor System

A Python application for creating and managing digital chaos magick servitors. Servitors are autonomous thoughtforms created to perform specific tasks through intention and energy management.

## Features

- **Servitor Creation**: Create servitors with names, purposes, and automatically generated sigils
- **Sigil Generation**: Generate sigils using witch wheel or random positioning
- **Charging System**: Multiple charging methods (visualization, repetition, ritual)
- **Task Execution**: Define and execute tasks for servitors (file operations, reminders, data processing)
- **Maintenance**: Energy decay tracking, feeding routines, and health monitoring
- **Dismissal Protocol**: Proper servitor dismissal with archiving
- **Dual Interface**: Both GUI and CLI modes available

## Installation

1. Ensure Python 3.8+ is installed
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### GUI Mode

Launch the graphical interface:

```bash
# Recommended: Run as a module
python -m servitor --gui
# or simply (auto-detects GUI mode on macOS/Windows)
python -m servitor

# Alternative: Run directly (also works)
python servitor/gui.py
```

The GUI provides:
- Visual servitor management dashboard
- Sigil display and charging interface
- Task execution panel
- Health monitoring

### CLI Mode

Use the command-line interface:

```bash
# Recommended: Run as a module
python -m servitor --cli
# or
python -m servitor.cli

# Alternative: Run directly (also works)
python servitor/cli.py
```

#### Available Commands

**Create a servitor:**
```bash
python -m servitor.cli create "MyServitor" "To help me focus on coding" --sigil-type witch_wheel --initial-charge 0
```

**List all servitors:**
```bash
python -m servitor.cli list
python -m servitor.cli list --status active
```

**Show servitor details:**
```bash
python -m servitor.cli show "MyServitor"
```

**Charge a servitor:**
```bash
python -m servitor.cli charge "MyServitor" 25.0 --method manual
```

**Activate a servitor:**
```bash
python -m servitor.cli activate "MyServitor"
```

**Feed a servitor:**
```bash
python -m servitor.cli feed "MyServitor" --amount 10.0
```

**Add a task to a servitor:**
```bash
python -m servitor.cli add-task "MyServitor" "Daily Reminder" "Remind me to code" reminder
```

**Execute tasks:**
```bash
python -m servitor.cli execute "MyServitor"
python -m servitor.cli execute "MyServitor" --task "Daily Reminder"
```

**Check health:**
```bash
python -m servitor.cli health
python -m servitor.cli health "MyServitor"
```

**Dismiss a servitor:**
```bash
python -m servitor.cli dismiss "MyServitor" --reason "Task complete"
```

## Servitor Concepts

### Charge Level
Servitors have a charge level (0-100%) that represents their energy. Servitors need sufficient charge to activate (default threshold: 50%).

### Energy Decay
Servitors lose energy over time (default: 1% per day). Regular feeding or charging is needed to maintain them.

### Tasks
Servitors can be assigned tasks:
- **Reminder**: Display reminders
- **File Operation**: Create, read, append, or delete files
- **Data Processing**: Process data (count, transform)
- **Log**: Log messages to files or console

### Charging Methods
- **Visualization**: Steady charging through visualization (1% per second)
- **Repetition**: High-intensity repetition charging (like Intention Repeater)
- **Ritual**: Slower but more powerful ritual charging

### Dismissal
When a servitor's purpose is complete, it should be properly dismissed through the dismissal protocol, which archives the servitor and cleans up resources.

## File Structure

```
servitor/
├── data/
│   ├── servitors/          # Individual servitor JSON files
│   ├── sigils/             # Generated sigil images
│   └── metadata.json        # Quick reference metadata
├── core/                   # Core functionality modules
└── ...
```

## Examples

### Creating a Focus Servitor

```bash
python -m servitor.cli create "Focus" "Help me maintain focus while coding" --sigil-type witch_wheel
python -m servitor.cli charge "Focus" 50.0
python -m servitor.cli activate "Focus"
python -m servitor.cli add-task "Focus" "Focus Reminder" "Remember to stay focused" reminder
```

### Creating a File Organizer Servitor

```bash
python -m servitor.cli create "Organizer" "Organize my files automatically"
python -m servitor.cli add-task "Organizer" "Log Activity" "Log file operations" log --parameters '{"log_file": "organizer.log"}'
```

## License

See LICENSE file for details.

## Notes

- Servitors are digital thoughtforms - their effectiveness depends on your belief and intention
- Regular maintenance (feeding/charging) is important to keep servitors active
- Dismiss servitors properly when their purpose is complete
- All servitor data is stored locally in JSON format


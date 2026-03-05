# File Map

## Top-level

### gui.py 🟡

- Entry point for the GUI.
- Composes UI and binds logic.
- **Danger**: Contains most of the interaction state.

### cli.py 🟢

- Command-line interface for the system.

## core/

### servitor.py 🔴

- Core data model (`Servitor`, `Task`).
- Central logic for activation and state transitions.

### charging.py 🟡

- Charging session management and method implementation.

### maintenance.py 🟡

- Energy decay and health check logic.

### storage.py 🔴

- Persistence layer. Handles loading/saving and applying decay on load.

### tasks.py 🟡

- Task execution logic and performance modifiers.

### sigil.py 🟢

- Sigil generation algorithms.

# Architecture

## Main Parts

- **Frontend (GUI)**: Python Tkinter application (`gui.py`) for user interaction.
- **Core Engine**: Business logic for servitor lifecycle (`core/`).
- **Storage Layer**: JSON-based persistence for servitors and sigils (`core/storage.py`).

## Communication

- The GUI talks to `Storage` to load/save servitors.
- `ChargingManager` and `MaintenanceManager` handle energy logic.
- `TaskExecutor` runs automated tasks when servitors are active.

## Design Decisions

- **Dynamic Energy Decay**: Charge level decays based on the servitor's status:
  - **Active**: 5% per day (high intensity).
  - **Dormant**: 1% per day (background state).
- **Maintenance Tracking**: Uses `last_maintenance_check` to ensure decay is applied exactly once per time period, calculating only the *new* time elapsed since the last check.
- **Evocation Cost with Cooldown**: A tiny energy cost (0.1% charge) is applied when a servitor is manifested, with a **10-minute cooldown** to prevent draining from rapid switching.
- **Background Maintenance Loop**: The GUI runs a background task every 60 seconds to apply decay to all servitors and refresh the list in real-time.

## App Type

This is a CRUD dashboard and automation tool for occult practices.

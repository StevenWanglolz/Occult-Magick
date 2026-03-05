# Data Flow

## Data Origin

- User input via GUI (creation, charging, tasks).
- Automatic energy decay (calculated on load).

## Storage & Movement

- Servitor data is stored as JSON in `data/servitors/`.
- Sigil images are generated and stored in `data/sigils/`.

## State

- Servitor state (Charge, Status) lives in the `Servitor` object at runtime and is persisted via `Storage`.
- **Background Updates**: A 5-second maintenance loop triggers updates for all servitors independently of user interaction.

## Lifecycle Steps

**Step 1: Loading a Servitor**

```python
# core/storage.py (lines 80-108)
def load_servitor(self, name: str, apply_decay: bool = True) -> Optional[Servitor]:
    # ... loads from JSON ...
    if apply_decay:
        from .maintenance import MaintenanceManager
        MaintenanceManager.apply_energy_decay(servitor)
```

**Step 2: Energy Decay Calculation**

```python
# core/maintenance.py (lines 18-41)
def calculate_energy_decay(servitor: Servitor, decay_rate: float = None) -> float:
    # ... 1% per day based on last_charged ...
```

**Step 3: Activation Check**

```python
# core/servitor.py (lines 120-131)
def can_activate(self) -> bool:
    return self.charge_level >= self.activation_threshold
```

# Modifier Effect Object

The `ModifierEffect` object represents a status effect applied when an item is consumed, including its stat bonuses and duration.

## Structure

```python
class ModifierEffect:
    id: str                   # Modifier row name (e.g., "Bread")
    display_name: str         # Localized name (e.g., "Bready Goodness")
    description: str          # Flavor description or effect summary
    lifetime: int             # Duration in seconds
    effects: Dict[str, float] # Stat bonuses (e.g., {"MaxStamina": 100})
```

## Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Internal RowName from `D_ModifierStates.json`. |
| `display_name` | `str` | Resolved human-readable name of the modifier. |
| `description` | `str` | Description text from the modifier state. |
| `lifetime` | `int` | Duration of the effect in seconds. |
| `effects` | `dict` | Key: Stat name, Value: Magnitude of the effect. |

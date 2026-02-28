# Tier Info Object

The `TierInfo` object captures the dynamic crafting tier of an item, including the logic used to derive it.

## Structure

```python
class TierInfo:
    base_tier: int            # Integer anchor (1-4)
    fractional_offset: float  # Talent tree depth (0.0 - 0.9)
    total_tier: float         # The effective tier (e.g., 2.3)
    anchor_bench: str         # The primary bench for the tier (e.g., "Crafting_Bench")
    is_harvested: bool        # True if Tier 0 (not crafted)
```

## Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `base_tier` | `int` | The tier of the lowest Master Bench requirement (1: Character, 2: Crafting Bench, 3: Machining Bench, 4: Fabricator). |
| `fractional_offset` | `float` | Shortest path distance in the talent tree from the anchor bench to this item's recipe talent. |
| `total_tier` | `float` | `base_tier + fractional_offset`. Used for sorting and display. |
| `anchor_bench` | `str` | The name of the bench that defines the integer tier. |
| `is_harvested` | `bool` | Set to `True` for Tier 0 items (items that never appear as recipe outputs). |

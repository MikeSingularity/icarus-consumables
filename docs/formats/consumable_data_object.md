# Consumable Data Object

The `ConsumableData` object is the primary internal representation of a food, drink, or medicine item in the Icarus Food Parser. It aggregates information from multiple game data files.

## Structure

```python
class IcarusItem:
    name: str                 # Internal name (e.g., "Food_Meat_Stew")
    display_name: str         # Localized name (e.g., "Meat Stew")
    description: str          # Item flavor text

class ConsumableData(IcarusItem):
    category: str             # Item category (Food, Drink, Animal Food, Medicine)
    base_stats: Dict[str, float] # Map of recovered stats (Health, Food, etc.)
    modifiers: List[ModifierEffect] # Active effects granted on consumption
    recipes: List[Recipe]     # Crafting recipes that produce this item
    tier_info: TierInfo       # Dynamic tier calculation results
```

## IcarusItem Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | `str` | The unique row name from `D_ItemsStatic.json`. |
| `display_name` | `str` | The translated name from `D_Itemable.json`. |
| `description` | `str` | Flavor text translated from `D_Itemable.json`. |

## ConsumableData Fields (Extends IcarusItem)

| Field | Type | Description |
| :--- | :--- | :--- |
| `category` | `str` | Determined by `ConsumableDataParser` based on tags and stats. |
| `base_stats` | `dict` | Key: Stat name (e.g., "Food"), Value: Recovery amount. |
| `modifiers` | `list` | A list of `ModifierEffect` objects associated with the item. |
| `recipes` | `list` | A list of `Recipe` objects that output this item. |
| `tier_info` | `TierInfo` | Metadata about the item's crafting tier level. |

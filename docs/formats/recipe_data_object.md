# Recipe and Ingredient Objects

The `Recipe` object represents a crafting process in Icarus, while the `Ingredient` object defines the specific items and quantities involved.

## Recipe Object

```python
class Recipe:
    id: str                   # Recipe row name (e.g., "Food_Meat_Stew")
    benches: List[str]        # List of benches where this can be crafted
    inputs: List[Ingredient]  # Items required for crafting
    outputs: List[Ingredient] # Items produced (usually includes the consumable)
    requirement: str          # Talent requirement (e.g., "Dough_Flatbread")
    character_req: str        # Character flag requirement (Special unlocks)
    session_req: str          # DLC or mission requirements
    energy_cost: float        # Required millijoules
```

### Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Internal name from `D_ProcessorRecipes.json`. |
| `benches` | `list` | Benches like `PotBellyStove`, `Kitchen_Stove`, etc. |
| `inputs` | `list` | List of `Ingredient` objects for crafting. |
| `outputs` | `list` | List of `Ingredient` objects produced. |
| `requirement` | `str` | Specific talent from `D_Talents.json` (if any). |
| `character_req`| `str` | Character flag from `D_CharacterFlags.json` (if any). |
| `session_req` | `str` | DLC or mission lock from `D_DLCPackageData.json` (if any). |
| `energy_cost` | `float` | Energy required for the recipe. |

## Ingredient Object

```python
class Ingredient:
    item: IcarusItem          # Reference to the shared item data
    count: int                # Quantity required or produced
```

### Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `item` | `IcarusItem` | Shared item metadata (Name, Display Name, Description). |
| `count` | `int` | Stack size or requirement count. |

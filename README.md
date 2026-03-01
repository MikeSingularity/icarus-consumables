# Icarus Food and Drinks Guide Generator

Automatically generates high-fidelity consumable guides for the game Icarus from extracted game data files. The tool processes JSON data files from the game and produces a structured `consumables_data.json` output.

## Overview

This tool parses Icarus game data to create detailed guides containing:
- All consumable items (food, drinks, medicine, animal feed)
- Nutritional values (food, water, health, oxygen recovery)
- Status effects and modifiers
- Crafting requirements and ingredients
- Crafting bench tier levels (0-4)
- Official English display names

**Current Data:** Processes **367 consumable items** from game data files

## Features

✅ **Automatic Display Name Translation** - Uses official English names from game files
✅ **Separated Effect Columns** - Individual columns for Food, Water, Health, Oxygen
✅ **Modifier Details** - Includes modifier names and detailed effects
✅ **JSON-Centric Output** - Generates a single, high-fidelity `consumables_data.json`
✅ **Smart Categorization** - Automatically categorizes into Food, Drink, Medicine, Animal Food
✅ **Dynamic Tier Calculation** - Determines crafting bench tier levels (0-4)
✅ **Recipe Matching** - Links items to their crafting recipes and ingredients

## Installation

### Prerequisites

- Python 3.7 or higher
- Game data files extracted from Icarus
- [uv](https://docs.astral.sh/uv/) for dependency management and execution

### Directory Structure

```
icarus-consumables/
├── main.py                     # Entry point (Main script)
├── unpacked_icarus_data/       # Game data files (JSON)
│   ├── Traits/
│   │   ├── D_Consumable.json   # Item stats and effects
│   │   └── D_Itemable.json     # Display names
│   ├── Crafting/
│   │   ├── D_ProcessorRecipes.json  # Crafting recipes
│   │   └── D_RecipeSets.json        # Crafting benches
│   └── Modifiers/
│       └── D_ModifierStates.json    # Modifier details
├── src/icarus_consumables/      # Package source
├── tests/                      # Test scripts
├── overrides/                  # Manual item overrides
└── README.md                   # This file
```

## Usage

### Basic Usage

Simply run the script via `uv`:

```bash
uv run python3 main.py
```

### Output Files

The script generates a single output file:

1. **consumables_data.json** - Structured JSON containing all item and modifier data.

### Expected Output

```
Generated Icarus Consumables Guide with 367 items
Output files generated:
  - JSON: consumables_data.json
```

## Output Format

### Structure

The output is a single JSON object containing:

1. **metadata** - Versioning and environment info.
2. **items** - List of all processed consumables.
3. **modifiers** - Detailed data for status effects (referenced by items).
- `Traits/D_Consumable.json`
- `Traits/D_Itemable.json`
- `Crafting/D_ProcessorRecipes.json`
- `Crafting/D_RecipeSets.json`
- `Modifiers/D_ModifierStates.json`

### File Not Found Errors

Ensure all required game data files exist in `unpacked_icarus_data/`:
- `Traits/D_Consumable.json`
- `Traits/D_Itemable.json`
- `Crafting/D_ProcessorRecipes.json`
- `Crafting/D_RecipeSets.json`
- `Modifiers/D_ModifierStates.json`

### Incorrect Item Names

If item names appear incorrect:
- Verify `D_Itemable.json` is from the current game version
- Check that the file contains `DisplayName` fields

### Items Missing from Output

The script excludes these placeholder items:
- `Vk1`, `Vk2`, `Vk3`
- `BasicFood`
- `AdvancedFood`
- `Meta_Bolt_Set_Larkwell_Piercing`

## Technical Details

### Display Name Translation

The script loads display names from `D_Itemable.json` using this mapping:
- Consumable name `Food_Bread` → Itemable entry `Item_Bread`
- Extracts from: `NSLOCTEXT("D_Itemable", "Item_Bread-DisplayName", "Bread")`
- Falls back to cleaned-up name if translation not found

### Recipe Matching

Recipes are matched using flexible name matching:
- Direct name matches
- Partial name matches
- Output name matches
- Handles variations like `Food_` and `Drink_` prefixes

### Modifier Effects

Extracts detailed effects from `D_ModifierStates.json`:
- Granted stats (stamina, health, resistances)
- Modifier variables
- Behavior information

## Project Structure

```
.
├── main.py                         # Entry point
├── src/icarus_consumables/                # Source code
├── README.md                       # This file
├── docs/                           # Technical documentation
├── tests/                          # Test scripts
├── unpacked_icarus_data/           # Game data (not included)
└── output/                         # Generated guides
```

## Known Limitations

- **Recipe Coverage:** Only 86 items have crafting recipes. Most items (281) are gathered or have no recipe data in the game files.
- **Medicine Category:** Includes all non-food/drink consumables (oxygen tanks, bandages, containers, etc.)

## Future Enhancements

Planned improvements (see `updates.md` for details):
- Automated weekly update checking
- Version control and diff tracking
- Multi-language support
- Web API for programmatic access
- Advanced filtering and search

## Contributing

When contributing:
1. Run all test scripts to verify changes
2. Update documentation if adding features
3. Follow existing code style and structure

## License

This tool is for personal use with legally obtained game data. Icarus game data is property of RocketWerkz.

## Version History

- **2026-02-09** - Major update: Separated effect columns, display name translation, CSV column reordering
- **2024** - Initial implementation with basic functionality

---

For questions or issues, refer to the `software_design_document.md` for technical details or `updates.md` for project status.

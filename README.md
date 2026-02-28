# Icarus Food and Drinks Guide Generator

Automatically generates comprehensive food, drink, and consumable guides for the game Icarus from extracted game data files. The tool processes JSON data files from the game and produces guides in multiple formats (Markdown, JSON, CSV, and ODS).

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
✅ **Multi-Format Output** - Generates Markdown, JSON, CSV, and ODS files
✅ **Smart Categorization** - Automatically categorizes into Food, Drink, Medicine, Animal Food
✅ **Dynamic Tier Calculation** - Determines crafting bench tier levels (0-4)
✅ **Recipe Matching** - Links items to their crafting recipes and ingredients

## Installation

### Prerequisites

- Python 3.7 or higher
- Game data files extracted from Icarus

### Required Python Packages

```bash
# Optional: For ODS (LibreOffice Calc) spreadsheet output
pip install openpyxl
```

### Directory Structure

```
icarus_food/
├── parse_food_data.py          # Main script
├── pak_files/                  # Game data files (required)
│   ├── Traits/
│   │   ├── D_Consumable.json   # Item stats and effects
│   │   └── D_Itemable.json     # Display names
│   ├── Crafting/
│   │   ├── D_ProcessorRecipes.json  # Crafting recipes
│   │   └── D_RecipeSets.json        # Crafting benches
│   └── Modifiers/
│       └── D_ModifierStates.json    # Modifier details
├── test_*.py                   # Test scripts
├── categories.md               # Category logic documentation
└── README.md                   # This file
```

## Usage

### Basic Usage

Simply run the script:

```bash
python3 main.py
```

### Output Files

The script generates four output files:

1. **icarus_food_guide.md** - Human-readable Markdown table
2. **icarus_food_guide.json** - Structured JSON for programmatic access
3. **icarus_food_guide.csv** - CSV for spreadsheet applications
4. **icarus_food_guide.ods** - LibreOffice Calc spreadsheet (requires openpyxl)

### Expected Output

```
Generated Icarus Food and Drinks Guide with 367 items
Output formats generated:
  - Markdown: icarus_food_guide.md
  - JSON: icarus_food_guide.json
  - CSV: icarus_food_guide.csv
  - ODS: icarus_food_guide.ods
```

## Output Format

### Column Structure

All output formats include these columns (in order):

1. **Category** - Item category (Animal Food, Food, Drink, Medicine)
2. **Item Name** - Official English display name
3. **Food** - Food recovery value
4. **Water** - Water recovery value
5. **Health** - Health recovery value
6. **Oxygen** - Oxygen recovery value
7. **Modifier** - Status effect modifier name
8. **Modifier Effects** - Detailed modifier effects
9. **Duration (seconds)** - Effect duration
10. **Ingredients** - Required crafting ingredients
11. **Crafting Bench** - Lowest tier crafting bench
12. **Tier** - Crafting bench tier level (0-4)

### Category Definitions

Items are automatically categorized using this logic:

- **Animal Food** - Provides BaseFoodRecovery AND contains "Animal" or "Omni" in name
- **Food** - Provides BaseFoodRecovery (but not Animal Food)
- **Drink** - Provides BaseWaterRecovery
- **Medicine** - All other consumables (bandages, oxygen, pastes, etc.)

### Tier Levels

Items are assigned tier levels based on the lowest crafting bench required:

- **Tier 0** - Hand-crafted or gathered (no crafting bench required)
- **Tier 1** - Campfire, Firepit, Character, Drying_Rack
- **Tier 2** - PotBellyStove, Cooking_Station, Crafting_Bench, T3_Smoker
- **Tier 3** - Kitchen_Stove, Kitchen_Bench, Machining_Bench, T4_Smoker, Seed_Extractor
- **Tier 4** - Electric_Stove, Advanced_Kitchen_Bench, Butchery_Bench, Fabricator, etc.

## Data Statistics

Based on current game data:

- **Total Items:** 367 consumables
  - Animal Food: 11 items
  - Food: 173 items
  - Drink: 20 items
  - Medicine: 163 items

- **Tier Distribution:**
  - Tier 0: 281 items (gathered/basic)
  - Tier 1: 24 items
  - Tier 2: 20 items
  - Tier 3: 33 items
  - Tier 4: 9 items

- **Recipe Coverage:**
  - Items with recipes: 86 items
  - Items without recipes: 281 items (gathered or special items)

## Testing

Run the included test scripts to validate functionality:

```bash
# Test tier assignment logic
python3 test_tier_assignment.py

# Test recipe matching
python3 test_recipe_matching.py

# Test recipe sets
python3 test_recipe_sets.py
```

## Updating Game Data

When Icarus releases weekly updates:

1. Extract new JSON files from the game's .pak files
2. Replace files in the `pak_files/` directory
3. Run the script again: `python3 main.py`
4. The guide will automatically update with new/changed items

## Troubleshooting

### Missing openpyxl

If you see `ODS: (requires openpyxl library)`:

```bash
pip install openpyxl
```

### File Not Found Errors

Ensure all required game data files exist in `pak_files/`:
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
├── src/icarus_food/                # Source code
├── README.md                       # This file
├── docs/                           # Technical documentation
├── tests/                          # Test scripts
├── pak_files/                      # Game data (not included)
└── output/                         # Generated guides
```

## Known Limitations

- **ODS Format:** Currently uses openpyxl (Excel library). Consider using odfpy for native ODS support.
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

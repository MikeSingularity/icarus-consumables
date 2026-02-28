# Claude Rules for Icarus Food Data Parser

## Project Overview

This project parses extracted Icarus game data files to generate comprehensive food, drink, and consumable guides in multiple formats (Markdown, JSON, CSV, ODS). It processes 366 consumable items with detailed nutritional values, status effects, crafting requirements, and tier levels.

## Directory Structure

```
icarus_food/
├── src/                    # Source code
│   └── parse_food_data.py  # Main parser script
├── tests/                  # Test scripts
│   ├── test_recipe_matching.py
│   ├── test_recipe_sets.py
│   └── test_tier_assignment.py
├── docs/                   # Documentation
│   ├── categories.md
│   ├── PROJECT_STRUCTURE.md
│   ├── software_design_document.md
│   └── updates.md
├── output/                 # Generated guide files
│   ├── icarus_food_guide.md
│   ├── icarus_food_guide.json
│   ├── icarus_food_guide.csv
│   └── icarus_food_guide.ods
├── unapcked_icarus_data/        # Game data - symlinked (not in repo, ~87 subdirs)
│   ├── Traits/
│   │   ├── D_Consumable.json    # Item stats and effects
│   │   └── D_Itemable.json      # English display names
│   ├── Crafting/
│   │   ├── D_ProcessorRecipes.json
│   │   └── D_RecipeSets.json
│   └── Modifiers/
│       └── D_ModifierStates.json
├── CLAUDE.md               # This file
└── README.md               # User-facing documentation
```

## Critical Code Conventions

### PEP8

- Use the PEP8 standard for Python code but set max line widths to 120 characters

### Include docstring

- Each function, class or method should have a docstring describing the utility of the class

### Use type hints

- Parameters and return values should use type hinting.  Use `dict` and `list`, not `Dict` and `List`.

### Use SOLID principals

- Use the SOLID design principals when writing code.

### Use DRY principals

- Use the DRY principal when writing code
- Code should be structured to be modular, focus on reuse and minimal redundancy.

### Path Resolution
- **ALWAYS** use `pathlib.Path` for file operations
- **NEVER** use string concatenation for paths
- All paths resolve relative to `PROJECT_ROOT` (parent of src/)

```python
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PAK_FILES_DIR = PROJECT_ROOT / 'pak_files'
OUTPUT_DIR = PROJECT_ROOT / 'output'
```

### Suppression List
Items in `SUPPRESS_LIST` are excluded from processing (not in actual game):

```python
SUPPRESS_LIST = [
    "Vk1", "Vk2", "Vk3",           # Test items
    "Raw_Food",                     # Placeholder
    "BasicFood",                    # Template
    "AdvancedFood",                 # Template
    "Meta_Bolt_Set_Larkwell_Piercing"  # Non-consumable
]
```

**DO NOT** remove items from this list without user approval.

### Display Name Translation
- Item names come from `D_Itemable.json` via NSLOCTEXT parsing
- Consumable name `Food_Bread` → Itemable entry `Item_Bread`
- Pattern: `NSLOCTEXT("D_Itemable", "Item_Name-DisplayName", "English Name")`
- Fallback: Clean up technical name if translation not found

### Recipe Matching Keywords
When matching recipes to consumables, use these keywords:

```python
['food', 'drink', 'beer', 'wine', 'soup', 'stew', 'pie', 'bread',
 'cake', 'cookie', 'jam', 'juice', 'milk', 'tea', 'coffee', 'cocoa',
 'smoothie', 'sorbet', 'pizza', 'pasta', 'salad', 'sandwich', 'roll',
 'muffin', 'pastry', 'tart', 'animal', 'feed']
```

Note: 'animal' and 'feed' are critical for Animal Food recipes.

## Data Processing Rules

### Category Assignment Logic
Items are categorized in this order (first match wins):

1. **Animal Food**: Has `BaseFoodRecovery` AND name contains "Animal" or "Omni"
2. **Food**: Has `BaseFoodRecovery` (but not Animal Food)
3. **Drink**: Has `BaseWaterRecovery`
4. **Medicine**: Everything else (oxygen, bandages, med kits, etc.)

### Tier Levels (0-4)
Based on lowest crafting bench required:

- **Tier 0**: Hand-crafted, gathered, or no recipe
- **Tier 1**: Campfire, Firepit, Character, Drying_Rack
- **Tier 2**: PotBellyStove, Cooking_Station, Crafting_Bench, T3_Smoker
- **Tier 3**: Kitchen_Stove, Kitchen_Bench, Machining_Bench, T4_Smoker, Seed_Extractor
- **Tier 4**: Electric_Stove, Advanced_Kitchen_Bench, Butchery_Bench, Fabricator

### Modifier Effects
- **86 unique modifier effect types** discovered in game data
- Effects are broken out into individual columns
- Columns are dynamically generated via first-pass collection
- All modifier columns appear at END of output (after base stats)

## Output Format Requirements

### Column Order
```
1. Item Name
2. Food
3. Water
4. Health
5. Oxygen
6. Duration (seconds)
7. Ingredients
8. Crafting Bench
9. Tier
10-95. [86 individual modifier effect columns, sorted alphabetically]
96. Modifier (name)
```

### Missing Value Formatting
- **Markdown**: Use `-` for missing/zero values
- **CSV**: Use blank/empty string
- **ODS**: Use blank/empty string
- **JSON**: Use `null` or omit key

### JSON Structure
```json
{
  "Items": [
    {
      "item_name": "Bread",
      "food": 100,
      "modifier": "Well_Fed",
      ...
    }
  ],
  "Modifiers": {
    "Well_Fed": {
      "effects": ["Staminaregen%: 25", ...],
      "duration": 900
    }
  }
}
```

This structure eliminates duplication - multiple items can reference the same modifier.

## Running and Testing

### Execute Parser
```bash
# From project root
python3 src/parse_food_data.py
```

**Expected output:**
- 366 items processed
- 86 unique modifier effect types
- 4 output files generated in output/

### Run Tests
```bash
python3 tests/test_tier_assignment.py
python3 tests/test_recipe_matching.py
python3 tests/test_recipe_sets.py
```

### Verification Checklist
- [ ] All Animal Food items have recipes (11 items)
- [ ] Item count is 366 (370 total - 4 suppressed)
- [ ] Output files generated in output/ directory
- [ ] No FileNotFoundError (paths resolve correctly)
- [ ] Markdown uses `-` for missing values
- [ ] CSV/ODS use blank for missing values
- [ ] Modifier columns appear at end

## Data Sources

### Game Data Files (pak_files/)
- **D_Consumable.json**: Item stats (food/water/health/oxygen recovery)
- **D_Itemable.json**: Official English display names
- **D_ProcessorRecipes.json**: Crafting recipes and ingredients
- **D_RecipeSets.json**: Crafting bench mappings
- **D_ModifierStates.json**: Status effect details

**IMPORTANT**: pak_files/ directory is NOT in version control. These are extracted from Icarus game .pak files.

### Expected Item Counts
- **Total**: 366 consumables (370 minus 4 suppressed)
  - Animal Food: 11 items
  - Food: 172 items
  - Drink: 20 items
  - Medicine: 163 items

### Known Limitations
- Only 86 items have crafting recipes
- 280 items are gathered or have no recipe data
- Medicine category is broad (includes oxygen tanks, bandages, containers)

## When Making Changes

### Before Modifying Code
1. Read the relevant source file first
2. Check docs/ for design decisions
3. Consider impact on all 4 output formats
4. Verify change doesn't break path resolution

### After Modifying Code
1. Run parser: `python3 src/parse_food_data.py`
2. Check item count is still 366
3. Verify all 4 output files generate
4. Spot-check Animal Food recipes present
5. Run relevant test scripts
6. Update docs/ if behavior changes
7. Update README.md version history

### Documentation Updates
When adding features or fixing bugs:
- Update `docs/updates.md` with changes
- Update `docs/software_design_document.md` if architecture changes
- Update README.md version history with date and description
- Add learnings to `.claude/memory/MEMORY.md` if applicable

## Project Phases (Complete)

✅ **Phase 1**: Basic parsing and markdown output
✅ **Phase 2**: Multi-format output (JSON, CSV, ODS)
✅ **Phase 3**: Display name translation
✅ **Phase 4**: Separated effect columns, modifier breakdown
⏸️ **Phase 5**: Automation system (deferred)

## Don't Do This

❌ **Don't** use string concatenation for file paths
❌ **Don't** remove items from SUPPRESS_LIST without approval
❌ **Don't** commit pak_files/ directory
❌ **Don't** use "N/A" for missing values (use `-` or blank)
❌ **Don't** change column order without discussion
❌ **Don't** modify category assignment logic without updating docs
❌ **Don't** assume all items have recipes (most are gathered)
❌ **Don't** use relative imports - paths resolve from PROJECT_ROOT

## Common Issues

### "FileNotFoundError: pak_files/..."
- Verify pak_files/ directory exists
- Check that game data was extracted
- Ensure paths use Path objects, not strings

### "Wrong item count (not 366)"
- Check if SUPPRESS_LIST was modified
- Verify all 4 suppressed items are excluded
- Check if game data files updated

### "Animal Food missing recipes"
- Verify 'animal' and 'feed' in recipe matching keywords
- Check D_ProcessorRecipes.json has Animal Feed entries

### "Paths don't resolve"
- Ensure using Path(__file__).parent approach
- Never use os.getcwd() - not reliable
- All paths relative to PROJECT_ROOT

## Future Enhancements (Not Started)

These are documented but **NOT implemented** (Phase 5):
- Automated weekly update checking
- Version control and diff tracking
- Multi-language support
- Web API
- Advanced filtering

**Do not implement these** without explicit user approval.

---

**Last Updated**: 2026-02-09
**Current Status**: Production-ready, all core features complete

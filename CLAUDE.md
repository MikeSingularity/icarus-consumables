This project parses extracted Icarus game data files to generate a comprehensive `consumables_data.json` guide. It processes 300+ consumable items with detailed nutritional values, status effects, crafting requirements, and tier levels.

## Directory Structure

```
icarus-consumables/
├── src/icarus_consumables/  # Modular package source
├── tests/                  # Test scripts (v3 Integrity Suite)
├── docs/                   # Documentation
├── output/                 # Generated .json only
├── unpacked_icarus_data/   # Game data (JSON, ~87 subdirs)
├── overrides/              # JSON override templates
├── main.py                 # Primary entry point
├── CLAUDE.md               # This file
└── README.md               # User-facing documentation
```

## Critical Code Conventions

### PEP8

- Max line width: **120 characters**.

### Documentation

- Mandatory **tall** docstrings for all classes and functions.

### Typing

- Use type hints. Favor `dict` and `list` (Python 3.14+).

### Path Resolution

- **ALWAYS** use `icarus_consumables.utils.path_resolver.resolve_path`.
- **NEVER** use string concatenation or hardcoded relative climbs.

```python
from icarus_consumables.utils.path_resolver import resolve_path

DATA_DIR = resolve_path('unpacked_icarus_data')
OUTPUT_DIR = resolve_path('output')
```

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

### JSON Structure
```json
{
  "metadata": {
    "parser_version": "v2.1.0",
    "game_version": "TBD"
  },
  "items": [
    {
      "name": "Food_Bread",
      "display_name": "Bread",
      "food": 100,
      "modifiers": [
        {
          "id": "Well_Fed",
          "display_name": "Well Fed",
          "lifetime": 900
        }
      ],
      ...
    }
  ]
}
```

## Running and Testing

### Execute Parser
```bash
# From project root
uv run python3 main.py
```

**Expected output:**
- 300+ items processed
- Successful generation of `output/consumables_data.json`

### Run Tests
```bash
uv run python3 tests/verify_integrity.py
```

### Verification Checklist
- [x] All Animal Food items have recipes or are harvested
- [x] Item count reflects game data (300+ items)
- [x] Canary items (Meat, Berry, Medicine, etc.) verified present
- [x] Output file correctly named `consumables_data.json`
- [x] No FileNotFoundError (paths resolve via `unpacked_icarus_data/`)

## Data Sources

### Game Data Files (unpacked_icarus_data/)
- **D_Consumable.json**: Item stats (food/water/health/oxygen recovery)
- **D_Itemable.json**: Official English display names
- **D_ProcessorRecipes.json**: Crafting recipes and ingredients
- **D_RecipeSets.json**: Crafting bench mappings
- **D_ModifierStates.json**: Status effect details

**IMPORTANT**: `unpacked_icarus_data/` directory is NOT in version control. These are extracted from Icarus game .pak files.

### Expected Item Counts
- **Total**: 328 consumables
  - Animal Food: 11 items
  - Food: 172 items
  - Drink: 20 items
  - Medicine: 125 items

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
1. Run parser: `uv run python3 main.py`
2. Check item count is at least 300
3. Verify `consumables_data.json` generates correctly
4. Run integrity suite (Canary Testing): `uv run python3 tests/verify_integrity.py`
5. Update docs/ if behavior changes

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
❌ **Don't** remove items from `overrides/` without approval
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

### "Low item count (under 300)"
- Check if `overrides/` were modified
- Verify `Fillable` equipment is auto-suppressed
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

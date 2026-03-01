# Icarus Food Guide Updates

This document tracks the current state of the project and lists changes needed to improve the Icarus Food and Drinks Guide.

## Current Project Status (as of 2026-02-09)

### ✅ Completed Implementation

**Phase 1-4: Core Functionality (COMPLETE)**
- ✅ Category assignment logic (Animal Food, Food, Drink, Medicine)
- ✅ Dynamic tier calculation (Tier 0-4 based on crafting benches)
- ✅ Item validation (excludes BasicFood, AdvancedFood, etc.)
- ✅ Recipe matching with flexible name handling
- ✅ Modifier integration from D_ModifierStates.json
- ✅ Multiple output formats: Markdown, JSON, CSV, ODS
- ✅ **Display name translation from D_Itemable.json** (NEW 2026-02-09)
- ✅ **Separated effect columns** - Food, Water, Health, Oxygen, Modifier, Modifier Effects (NEW 2026-02-09)
- ✅ **CSV column reordering** - Category as first column (NEW 2026-02-09)
- ✅ Comprehensive effects display with modifiers and durations

**Current Output:**
- Total items processed: **367** (out of 370 in D_Consumable.json)
  - Animal Food: 11 items
  - Food: 173 items
  - Drink: 20 items
  - Medicine: 163 items (includes oxygen, bandages, pastes, containers)
- Output file sizes: CSV (45K), JSON (133K), Markdown (52K), ODS (23K)

**Test Coverage:**
- ✅ Recipe matching tests passing
- ✅ Tier assignment tests passing
- ✅ Recipe sets tests created
- ✅ Data validation complete (367 items, 86 with recipes)

**Documentation:**
- ✅ README.md created with complete installation and usage guide
- ✅ Software design document updated
- ✅ All test scripts functional

### ❌ Not Yet Implemented

**Phase 5: Automation (NOT STARTED)**
- ❌ Weekly game data update checking
- ❌ Version control for game data
- ❌ Diff functionality for tracking changes
- ❌ Batch scripts for automated execution
- ❌ Scheduling integration (cron/Task Scheduler)

## ✅ Completed Changes (2026-02-09)

### 1. Output Format Improvements ✅ COMPLETE

**1.1 Separate Effect Columns ✅**
- ✅ Split into dedicated columns: Food, Water, Health, Oxygen, Modifier, Modifier Effects
- ✅ Individual columns for each stat type
- ✅ Duration (seconds) column maintained
- ✅ All output formats updated (Markdown, JSON, CSV, ODS)

**1.2 CSV Column Order Fix ✅**
- ✅ Category moved to first column for better sorting/filtering
- ✅ Column order implemented:
  1. Category
  2. Item Name
  3. Food
  4. Water
  5. Health
  6. Oxygen
  7. Modifier
  8. Modifier Effects
  9. Duration (seconds)
  10. Ingredients
  11. Crafting Bench
  12. Tier

### 2. Display Name Translation ✅ COMPLETE

**Implementation completed:**
- ✅ Loads D_Itemable.json at startup
- ✅ Builds mapping dictionary: consumable name → display name
- ✅ Extracts display name from NSLOCTEXT using regex
- ✅ Uses proper display names from game data
- ✅ Fallback to cleanup logic if display name not found

**Results:**
- ✅ Accurate official names: "Wild Berry", "Steamed Fish", "Young Coconut"
- ✅ Handles special cases automatically
- ✅ No manual name fixes needed
- ✅ Future-proof for new items

### 3. Data Validation and Testing ✅ COMPLETE

**3.1 Item Categorization Verified ✅**
- ✅ Medicine category (163 items) reviewed and documented
- ✅ Non-consumables (oxygen tanks, containers) documented as intended
- ✅ Category logic validated and working correctly

**3.2 Recipe Matching Validated ✅**
- ✅ All items with recipes properly matched
- ✅ Items missing ingredient/crafting data identified (281 gathered items)
- ✅ Tier assignments verified accurate

**3.3 Comprehensive Testing ✅**
- ✅ All test scripts run and passing
- ✅ Complete pipeline tested and functional
- ✅ Validation report generated

### 4. Documentation Updates ✅ COMPLETE

**4.1 Software Design Document ✅**
- ✅ Phases 1-4 marked as complete
- ✅ Current architecture documented
- ✅ Implementation status section added

**4.2 Usage Documentation ✅**
- ✅ README.md created with:
  - Installation instructions
  - Dependencies (openpyxl for ODS)
  - How to run the script
  - How to update game data
  - Output format documentation
  - Troubleshooting guide
  - Technical details

### 5. Future Enhancements (BACKLOG)

**5.1 Automation System (Phase 5)**
- Implement weekly update checking
- Add version control for game data
- Create diff reports for changes
- Build automated execution scripts
- Set up scheduling

**5.2 ODS Format Fix**
- Current implementation uses openpyxl (Excel library)
- Consider switching to odfpy for proper LibreOffice Calc (.ods) format

**5.3 Additional Features**
- Language localization support (multiple languages in D_Languages.json)
- Advanced filtering options
- Data visualization charts
- Web API for programmatic access
- Search functionality

## Implementation Status

1. ✅ **COMPLETE:** Separate effect columns + CSV column reordering
2. ✅ **COMPLETE:** Display name translation from D_Itemable.json
3. ✅ **COMPLETE:** Data validation and comprehensive testing
4. ✅ **COMPLETE:** Documentation updates (README, usage guide)
5. ❌ **FUTURE:** Automation system (Phase 5) - Deferred

## Data Files Reference

**Required Input Files:**
- `pak_files/Traits/D_Consumable.json` - Item effects and stats (370 items)
- `pak_files/Crafting/D_ProcessorRecipes.json` - Crafting recipes
- `pak_files/Crafting/D_RecipeSets.json` - Crafting benches/stations
- `pak_files/Modifiers/D_ModifierStates.json` - Modifier details
- `pak_files/Traits/D_Itemable.json` - Display names and item metadata

**Generated Output Files:**
- `icarus_consumables_guide.md` - Markdown format (52K, updated format)
- `icarus_consumables_guide.json` - JSON format (133K, updated structure)
- `icarus_consumables_guide.csv` - CSV format (45K, Category-first ordering)
- `icarus_consumables_guide.ods` - LibreOffice Calc spreadsheet (23K)
- `README.md` - Installation and usage documentation

## Project Summary

**Status:** Production-ready for manual use. Phases 1-4 complete.

**Key Features:**
- Processes 367 consumable items with official English names
- Separates stats into individual columns for better analysis
- Category-first CSV ordering for improved sorting/filtering
- Multiple output formats (Markdown, JSON, CSV, ODS)
- Comprehensive test coverage and validation
- Complete documentation (README, design doc, this file)

**Notes:**
- The guide includes ALL consumables (food, drinks, medicine, oxygen, containers, etc.)
- Total of 367 items processed from 370 available (3 excluded: BasicFood, AdvancedFood, Meta_Bolt_Set_Larkwell_Piercing)
- Medicine category includes utility items like oxygen tanks, bandages, canteens
- 86 items have crafting recipes, 281 are gathered or special items
- Tool can be easily updated when Icarus releases weekly patches

## 🏗 Proposed Changes: SOLID/DRY Refactoring (v2) [/] IN-PROGRESS
*Goal: Move from monolithic script to a modular, service-oriented architecture with dynamic tiering.*

### 1. Architectural Strategy
- ✅ Service Layer: Separate data loading, mapping, and generation.
- ✅ Domain Models: Formal `IcarusItem`, `ConsumableData`, and `Recipe` objects.
- ✅ Dynamic Tiering: Replace hardcoded maps with Talent Tree path-finding.
- ✅ Requirement Extraction: Specifically denote skill/flag unlocks (e.g. `Flatbread Dough`).

### 2. Next Steps
- [ ] Initialize modular `src/` directory structure.
- [ ] Implement `IcarusTierMapper` using `pak_files/Talents/D_Talents.json`.
- [ ] Migrate Categorization logic to `ConsumableDataParser`.
- [ ] Build polymorphic output generators.

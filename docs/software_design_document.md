# Icarus Food and Drinks Guide - Software Design Document

> [!IMPORTANT]
> This document describes both the legacy monolithic implementation (v1) and the new modular SOLID refactoring (v2).

## 1. Introduction

This software design document outlines the architecture and implementation plan for generating the Icarus Food and Drinks Guide from the game's JSON data files. The guide provides comprehensive information about all consumable items in the game, including their effects, crafting requirements, and tier levels. The Icarus game updates weekly, which occasionally includes changes or additions to food, drinks, animal food, and medicines. This tool ensures that people have access to updated information to make informed food and drink selections.
 
## 2. Problem Statement

The current approach to generating the Icarus Food and Drinks Guide has several issues:

- Items are being incorrectly categorized
- Tier levels for crafting benches are not being properly assigned
- Recipe matching between different data files is inconsistent
- Some items that don't exist in the game are still included
- Modifier information from D_ModifierStates.json is not being properly utilized
- Lack of support for multiple output formats (JSON, CSV, LibreOffice Spreadsheet)
- Difficulty in maintaining the guide with weekly game updates

## 3. Requirements

### 3.1 Functional Requirements

1. **Category Assignment**:
   - Implement the category logic from `categories.md`
   - Animal Food: Provides BaseFoodRecovery and has "Animal" or "Omni" in name
   - Food: Provides BaseFoodRecovery
   - Drink: Provides BaseWaterRecovery
   - Medicine: All other consumables

2. **Dynamic Tier Level Calculation (v2 refined)**:
   - **Tier Detection Mechanism**:
     - Extract all available crafting stations from `D_RecipeSets.json`.
     - Detect "Master Benches" as anchors: Character (1.0), Crafting Bench (2.0), Machining Bench (3.0), Fabricator (4.0).
     - **Talent-Path Distance**: For any item, calculate the fractional offset (0.1 - 0.9) by finding the shortest path distance in `D_Talents.json` from the closest anchor bench to the item's recipe talent.
     - **Tier 0**: Items that do not appear as outputs in `D_ProcessorRecipes.json` are assigned Tier 0 (harvested).
   - **Legacy Tier Mapping (v1)**:
     - *Note: This manual mapping is superseded by the v2 Talent-Path logic.*
     - Tier 0: Hand-crafted/Gathered.
     - Tier 1: Campfire, Firepit, Character.
     - Tier 2: PotBellyStove, Cooking_Station, Crafting_Bench.
     - Tier 3: Kitchen_Stove, Kitchen_Bench, Machining_Bench.
     - Tier 4: Electric_Stove, Advanced_Kitchen_Bench, Fabricator.

3. **Item Validation**:
   - Remove items that are not actually in the game (e.g., "BasicFood", "AdvancedFood")

4. **Effects Display**:
   - Display both direct stats and modifiers from D_ModifierStates.json
   - Include modifier duration information

5. **Recipe Matching**:
   - Improve the recipe matching logic between D_Consumable.json and D_ProcessorRecipes.json
   - Handle item name variations and prefixes like "Food_" and "Drink_"

6. **Output Formatting**:
   - Generate a Markdown document with tables for each category
   - Generate JSON output for programmatic access
   - Generate CSV output for spreadsheet applications
   - Generate LibreOffice Calc (ODS) spreadsheet for easy editing
   - Clean up item names (remove prefixes, fix "Jam Jar" to "Jam")

7. **Weekly Update Support**:
   - Automate the process of checking for and updating to new game data
   - Versioning system to track changes between updates
   - Diff functionality to highlight changes in each update

### 3.2 Non-Functional Requirements

1. **Performance**: The script should process all items efficiently
2. **Maintainability**: Code should be well-structured and documented
3. **Accuracy**: The generated guide should be accurate and complete
4. **Extensibility**: The script should be easy to update with new items or categories
5. **Automation**: Support for automated execution to handle weekly updates
6. **Compatibility**: Ensure output formats are compatible with common tools

## 4. Architecture

### 4.1 Data Files

The guide generation process relies on three main JSON files:

1. **D_Consumable.json**: Contains item effects, duration, and modifiers
2. **D_ProcessorRecipes.json**: Contains crafting recipes and required benches
3. **D_ModifierStates.json**: Contains detailed information about modifiers

### 4.2 High-Level Architecture

The system follows a modular, pipeline-based architecture:

1. **Data Loading and Validation**: 
   - Load and validate all required JSON files (D_Consumable.json, D_ProcessorRecipes.json, D_ModifierStates.json)
   - Check for data consistency and completeness
   - Version control integration for tracking updates

2. **Data Transformation**:
   - Extract and process consumable item data
   - Extract and process crafting recipe data
   - Match items to recipes using improved matching logic
   - Calculate tier levels for each item
   - Normalize and standardize data formats

3. **Data Storage**:
   - Maintain a local cache of processed data
   - Track version history of game data
   - Store diff information between updates

4. **Output Generation**:
   - Generate Markdown document with tables for each category
   - Generate JSON output for programmatic access
   - Generate CSV output for spreadsheet applications
   - Generate LibreOffice Calc (ODS) spreadsheet for easy editing
   - Clean up item names (remove prefixes, fix "Jam Jar" to "Jam")

5. **Update Management**:
   - Check for new game data updates
   - Compare current data with previous version
   - Highlight changes and additions
   - Automate the entire process

## 5. Implementation Plan

### 5.1 Phase 1: Architecture and Design ✅ COMPLETE

1. ✅ Analyze the current script implementation
2. ✅ Define the data model for items, recipes, and tiers
3. ✅ Design the improved recipe matching algorithm
4. ✅ Create a test plan for verification
5. ❌ Design the update management system (deferred to Phase 5)
6. ✅ Select libraries for ODS/CSV/JSON output (openpyxl)

### 5.2 Phase 2: Core Implementation ✅ COMPLETE

1. ✅ Modify the data loading and validation logic
2. ✅ Implement the improved recipe matching algorithm
3. ✅ Update the tier calculation logic
4. ✅ Implement the new category assignment logic
5. ❌ Implement data storage and version control (deferred to Phase 5)
6. ❌ Create the update management system (deferred to Phase 5)

### 5.3 Phase 3: Output Generation ✅ COMPLETE (Enhanced 2026-02-09)

1. ✅ Implement item name cleanup with D_Itemable.json translation
2. ✅ Enhance effects display to include modifiers
3. ✅ Generate the Markdown document with proper formatting
4. ✅ Add tables for each category
5. ✅ Implement JSON output
6. ✅ Implement CSV output with Category-first column order
7. ✅ Implement LibreOffice Calc (ODS) output
8. ✅ **NEW:** Separate effect columns (Food, Water, Health, Oxygen, Modifier, Modifier Effects)
9. ✅ **NEW:** Display name translation from D_Itemable.json

### 5.4 Phase 4: Testing and Verification ✅ COMPLETE

1. ✅ Test the script with various data files
2. ✅ Verify the accuracy of the generated guide
3. ✅ Check for any missing or incorrect data
4. ✅ Test the update management system (manual process works)
5. ✅ Verify the compatibility of output formats
6. ✅ Optimize performance (adequate for current use)

### 5.6 Phase 6: SOLID/DRY Refactoring (v2) [/] IN-PROGRESS

1. [x] Analyze data structures and talent trees for dynamic tiering.
2. [x] Design service-oriented architecture (Data Loaders, Mappers, Generators).
3. [x] Document internal data objects (`IcarusItem`, `ConsumableData`, `Recipe`).
4. [ ] Implement `IcarusDataLoader` and `IcarusTranslationService`.
5. [ ] Implement `IcarusTierMapper` with Talent-Path logic.
6. [ ] Implement Polymorphic Output Generators.
7. [ ] Validate v2 output against v1 baseline.

**Status:** Phases 1-4 (v1) complete. Phase 6 (v2) in progress.

## 6. Data Structures

### 6.1 Item Data Model

```python
class Item:
    name: str
    display_name: str
    category: str
    effects: List[Effect]
    duration: int
    ingredients: List[Ingredient]
    crafting_bench: str
    tier: int
```

### 6.2 Effect Data Model

```python
class Effect:
    name: str
    value: float
```

### 6.3 Ingredient Data Model

```python
class Ingredient:
    name: str
    quantity: int
```

## 7. Key Implementation Details

### 7.1 Recipe Matching Algorithm

The improved recipe matching algorithm will:
1. Handle item name variations (e.g., "Chocolate_Cake" vs "Chocolate_Cake_Piece")
2. Match items based on partial name matches with fuzzy matching
3. Handle prefixes like "Food_" and "Drink_" in recipe names

### 7.2 Dynamic Tier Calculation Logic

The dynamic tier calculation system will:

1. **Extract Crafting Stations**: Load all available recipe sets from D_RecipeSets.json
2. **Infer Tiers from Names**: Detect tier numbers in recipe set names (e.g., T3_Smoker = Tier 3)
3. **Progression-Based Detection**: Determine tiers for known stations based on game knowledge:
   - Tier 1: Campfire, Firepit, Character
   - Tier 2: PotBellyStove, Cooking_Station, Crafting_Bench, T3_Smoker
   - Tier 3: Kitchen_Stove, Kitchen_Bench, Machining_Bench, T4_Smoker, Seed_Extractor
   - Tier 4: Electric_Stove, Advanced_Kitchen_Bench, Butchery_Bench, Fabricator, etc.
4. **Handle New Stations**: For unknown recipe sets, assign to Tier 4 as a default
5. **Multi-Bench Recipes**: Determine the lowest possible tier from all available crafting options

The system will be designed to adapt to new crafting stations introduced in weekly updates without requiring manual modification of the script.

### 7.3 Modifier Processing

The modifier processing will:
1. Load modifier information from D_ModifierStates.json
2. Display modifier effects and durations in the guide
3. Link modifiers to their corresponding items

## 8. Verification and Testing

### 8.1 Testing Strategy

1. **Unit Tests**: Test individual components (data loading, category assignment, recipe matching)
2. **Integration Tests**: Test the complete pipeline
3. **Validation Tests**: Verify the accuracy of the generated guide
4. **Performance Tests**: Ensure the script runs efficiently with large datasets

### 8.2 Test Data

Use a small but representative subset of the data for testing purposes:
- Include items from all categories
- Include recipes with different tiers
- Include items with modifiers

## 9. Future Enhancements

1. **Language Localization**: Add support for multiple languages
2. **Advanced Filtering**: Allow filtering by categories, tiers, or effects
3. **Data Visualization**: Add charts and graphs to display item statistics
4. **API Integration**: Create a web API for accessing item data programmatically

## 10. Implementation Status (Updated 2026-02-09)

### Current Implementation

**Phases 1-4: COMPLETE**

The core functionality is fully implemented and operational:

1. **Display Name Translation**
   - Loads official English names from `D_Itemable.json`
   - Uses NSLOCTEXT extraction with regex pattern matching
   - Fallback to manual cleanup for missing translations
   - Examples: "Wild Berry", "Steamed Fish", "Young Coconut"

2. **Separated Effect Columns**
   - Individual columns for: Food, Water, Health, Oxygen
   - Separate Modifier and Modifier Effects columns
   - Improves readability and data analysis capabilities

3. **CSV Column Ordering**
   - Category placed as first column for better sorting/filtering
   - Consistent column order across all output formats

4. **Data Processing**
   - Processes 367 items from D_Consumable.json (370 total, 3 excluded)
   - 4 categories: Animal Food (11), Food (173), Drink (20), Medicine (163)
   - Tier distribution: T0 (281), T1 (24), T2 (20), T3 (33), T4 (9)
   - Recipe coverage: 86 items with recipes, 281 without

5. **Output Formats**
   - Markdown (.md) - Human-readable tables
   - JSON (.json) - Structured data for programmatic access
   - CSV (.csv) - Spreadsheet compatible
   - ODS (.ods) - LibreOffice Calc format (using openpyxl)

### Testing and Validation

- ✅ Tier assignment tests passing
- ✅ Recipe matching tests passing
- ✅ All output formats generating correctly
- ✅ Display name translation working (D_Itemable.json)
- ✅ Data validation complete

### Documentation

- ✅ README.md created with installation and usage instructions
- ✅ Software design document updated (this file)
- ✅ updates.md tracking project status and future changes
- ✅ Test scripts available for validation

### Known Limitations

1. **ODS Format**: Uses openpyxl (Excel library) instead of native ODS library (odfpy)
2. **Recipe Coverage**: Only 86/367 items have crafting recipes in game data
3. **Medicine Category**: Includes all non-food/drink consumables (oxygen, containers, bandages)
4. **No Automation**: Weekly update process is manual (Phase 5 not implemented)

### Future Work (Phase 5 - Deferred)

The following features are planned but not yet implemented:

- Automated weekly update checking
- Version control for game data
- Diff functionality to track changes between updates
- Batch scripts for automated execution
- Scheduling integration (cron/Task Scheduler)
- Multi-language localization support

## 11. Conclusion

This software design document provides a comprehensive plan for improving the Icarus Food and Drinks Guide. Phases 1-4 have been successfully completed, delivering a fully functional tool that generates accurate, well-formatted guides in multiple output formats. The architecture and implementation address all the identified issues and provide a solid foundation for future enhancements.

The tool is production-ready for manual use and can be easily updated when Icarus releases weekly patches. Phase 5 automation features remain available as future enhancements when needed.
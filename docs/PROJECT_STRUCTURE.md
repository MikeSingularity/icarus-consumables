# Icarus Food Guide - Project Structure

This document describes the organization of the project files and directories.

## Directory Structure

```
icarus_consumables/
├── main.py             # Main entry point
├── src/icarus_consumables/    # Modular source code
│   ├── models/         # Data objects
│   ├── services/       # Logic
│   ├── generators/     # Output (Markdown, JSON, CSV, ODS)
│   └── utils/          # Shared helpers
├── output/                 # Generated output files

│   └── consumables_data.json
├── docs/                   # Documentation
│   ├── categories.md       # Category logic definition
│   ├── software_design_document.md
│   └── updates.md          # Project status and changes
├── tests/                  # Test scripts
│   ├── test_recipe_matching.py
│   ├── test_tier_assignment.py
│   └── test_recipe_sets.py
├── unpacked_icarus_data/              # Game data files (extracted from Icarus)
│   ├── Traits/
│   ├── Crafting/
│   ├── Modifiers/
│   └── ...
├── README.md               # Main project documentation
└── imm/                    # Extraction tools

```

## Usage

### Running the Script

From the project root directory:

\`\`\`bash
python3 main.py
\`\`\`

This will generate all output files in the `output/` directory.

### Output Files

All generated guides are placed in the `output/` directory:

- **consumables_data.json** - JSON format with Items and Modifiers structure

### Testing

Run individual test scripts from the project root:

\`\`\`bash
python3 tests/test_tier_assignment.py
python3 tests/test_recipe_matching.py
\`\`\`

## File Descriptions

### Source Files

- **main.py** - entry point that launches the refactored ecosystem.
- **src/icarus_consumables/** - Contains all modular logic, models, and generators.

### Documentation

- **README.md** - Installation, usage, and overview
- **docs/software_design_document.md** - Technical design and architecture
- **docs/updates.md** - Current status and completed changes
- **docs/categories.md** - Category assignment logic

### Tests

- **test_tier_assignment.py** - Validates tier calculation logic
- **test_recipe_matching.py** - Tests recipe matching algorithm
- **test_recipe_sets.py** - Tests recipe set handling

## Data Flow

1. **Input**: Game data files in `pak_files/`
2. **Processing**: `main.py` entry point (using `src/icarus_consumables/` services)
3. **Output**: Generated guides in `output/`

## Notes

- The script uses Path-based file access and can be run from any directory
- All paths are resolved relative to the script location
- Output files are always written to the `output/` directory
- Game data files remain in `unpacked_icarus_data/` directory

# Antigravity Development Guide: Icarus Food Data Parser

This guide summarizes project-specific rules and logic optimized for development in the Antigravity editor.

## 🚀 Quick Actions (Workflows)
You can use the following workflows for common tasks:
- `/run-parser`: Execute the data processing script.
- `/test`: Run the test suite.
- `/verify`: Validate the integrity of generated output.

## 🛠 Coding Standards
- **Python**: PEP8 compliant, max line width **120 characters**.
- **Documentation**: Mandatory **tall** docstrings for all classes, functions, and methods.
  ```python
  def func():
      """
      Tall docstring format.
      """
  ```
- **Typing**: Use type hints. Favor `dict` and `list` over `Dict` and `List` (Python 3.14+).
- **Environment**: Honor `pyproject.toml` and use `uv` for dependency management.
- **Paths**: **ALWAYS** use `pathlib.Path`. Never concatenate strings for paths.

## 🏗 Project Architecture
- **Root Directory**: All paths resolve relative to `PROJECT_ROOT`.
- **Source**: `src/` (Modular package).
- **Tests**: `tests/`.
- **Output**: `output/` (Markdown, JSON, CSV, ODS).
- **Pak Files**: `pak_files/` (External game data, NOT committed).

## 📊 Core Logic
### Category Order
1. **Animal Food**: `BaseFoodRecovery` + "Animal/Omni" in name.
2. **Food**: `BaseFoodRecovery`.
3. **Drink**: `BaseWaterRecovery`.
4. **Medicine**: Default (Oxygen, Bandages, etc.).

### Tier Definition (v2 Dynamic)
- **Tier 0**: Harvested items (not craftable).
- **Fractional Tiers**: Calculated via `Talent-Path Distance` from Master Bench anchors:
  - **1.x**: Character
  - **2.x**: Crafting Bench
  - **3.x**: Machining Bench
  - **4.x**: Fabricator

## ⚠️ Important Constraints
- **SUPPRESS_LIST**: Do not modify without approval.
- **Item Count**: Must strictly be **366** consumables.
- **Missing Values**:
  - Markdown: `-`
  - CSV/ODS/JSON: Blank/Null.

---
*Derived from [CLAUDE.md](file:///home/mike/Projects/mike-singularity/icarus_food/CLAUDE.md)*

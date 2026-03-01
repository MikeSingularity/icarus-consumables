# Antigravity Development Guide: Icarus Food Data Parser

This guide summarizes project-specific rules and logic optimized for development in the Antigravity editor.

## 🚀 Quick Actions (Workflows)
You can use the following workflows for common tasks:
- `/run-parser`: Execute the data processing script via `uv run python3 main.py`.
- `/test`: Run the test suite via `uv run python3 tests/...`.
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
- **Root Directory**: All paths resolve via `icarus_consumables.utils.path_resolver`.
- **Source**: `src/icarus_consumables/` (Modular package).
- **Tests**: `tests/`.
- **Output**: `output/` (JSON-only).
- **Game Data**: `unpacked_icarus_data/` (JSON source).

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
- **Visibility Control**: Use JSON files in `overrides/` to suppress items (set `is_visible: false`).
- **Item Count**: Must be at least **300** consumables.
- **Integrity**: Must pass canary verification script (`tests/verify_integrity.py`).
    - **Missing Values**:
  - JSON: `null` or omit key.

---
*Derived from [CLAUDE.md]*

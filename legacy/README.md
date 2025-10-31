# Legacy Files

This directory contains files from the old project structure, archived for reference.

## Contents

- **README.old.md** - Original README before restructure (October 2025)
- **requirements*.txt** - Old pip requirements files (replaced by `pyproject.toml`)

## Migration Notes

As of October 31, 2025, SATCN has migrated to:
- **Modern src/ layout** - All code in `src/satcn/`
- **pyproject.toml** - Single source of truth for dependencies
- **CLI command** - `satcn` command installed via pip

### Old Structure → New Structure

```
pipeline/              → src/satcn/core/
tools/*gui*.py         → src/satcn/gui/
requirements*.txt      → pyproject.toml [project.dependencies]
test_*.py (root)       → scripts/
```

### Installing Dependencies

**Old way (deprecated):**
```bash
pip install -r requirements.txt
pip install -r requirements-grmr.txt
```

**New way:**
```bash
pip install -e .              # Base dependencies
pip install -e ".[grmr]"      # + GRMR-V3 support
pip install -e ".[t5]"        # + T5 support
pip install -e ".[dev]"       # + Dev tools
pip install -e ".[all]"       # Everything
```

## Reference

See `MIGRATION.md` in the root directory for complete migration guide.
See `RESTRUCTURE_SUMMARY.md` for detailed restructure notes.

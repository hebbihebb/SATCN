# SATCN Restructuring - Migration Guide

**Date:** October 31, 2025
**Branch:** `chore/cleanup-restructure`
**Status:** Complete - Ready for Review

## What Changed

This restructure reorganizes SATCN into a standard Python src/ layout for better maintainability, packaging, and development workflow.

### Directory Structure (Before → After)

```
BEFORE:
SATCN/
├─ pipeline/                  # Mixed location
│  ├─ pipeline_runner.py
│  ├─ filters/
│  └─ utils/
├─ tools/                     # GUI scattered
├─ test_*.py                  # Tests at root
├─ benchmark_*.py             # Scripts at root
├─ tests/                     # Some tests here
├─ requirements*.txt          # Multiple files

AFTER:
SATCN/
├─ src/satcn/                 # All app code
│  ├─ cli/main.py             # CLI entrypoint
│  ├─ gui/                    # GUI components
│  └─ core/                   # Pipeline logic
│     ├─ filters/
│     ├─ utils/
│     └─ pipeline_runner.py
├─ tests/                     # All tests
├─ scripts/                   # Dev/bench scripts
├─ data/samples/              # Sample inputs
├─ pyproject.toml             # Single config
└─ .pre-commit-config.yaml    # Code quality
```

## Breaking Changes

### 1. Import Paths

**Old:**
```python
from pipeline.pipeline_runner import PipelineRunner
from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter
from pipeline.utils.logging_setup import setup_logging
```

**New:**
```python
from satcn.core.pipeline_runner import PipelineRunner
from satcn.core.filters.grmr_v3_filter import GRMRV3GrammarFilter
from satcn.core.utils.logging_setup import setup_logging
```

### 2. CLI Usage

**Old:**
```bash
python -m pipeline.pipeline_runner --use-grmr input.md
```

**New:**
```bash
satcn --use-grmr input.md
# OR
python -m satcn.cli.main --use-grmr input.md
```

### 3. GUI Launching

**Old:**
```bash
python tools/pipeline_test_gui.py
python tools/grmr_v3_test_gui.py
```

**New:**
```bash
python -m satcn.gui.pipeline_test_gui
python -m satcn.gui.grmr_v3_test_gui
```

### 4. Test/Script Locations

**Old:**
```bash
python test_long_document_gpu.py
python benchmark_grmr_quality.py
```

**New:**
```bash
python scripts/test_long_document_gpu.py
python scripts/benchmark_grmr_quality.py
```

### 5. Dependencies

**Old:**
```bash
pip install -r requirements.txt
pip install -r requirements-grmr.txt
pip install -r requirements-t5.txt
```

**New:**
```bash
pip install -e .              # Base
pip install -e ".[grmr]"      # + GRMR-V3
pip install -e ".[t5]"        # + T5
pip install -e ".[all]"       # Everything
```

## Migration Steps for Contributors

### If You Have a Clone

```bash
# 1. Fetch latest changes
git fetch origin

# 2. Switch to new structure branch
git checkout chore/cleanup-restructure

# 3. Remove old virtual environments
rm -rf .venv .venv-gpu .venv310

# 4. Create fresh environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# 5. Install package (editable mode)
pip install -e ".[dev]"

# 6. Verify tests pass
pytest

# 7. Install pre-commit hooks
pre-commit install
```

### If You Have Local Changes

```bash
# 1. Stash your changes
git stash

# 2. Checkout new structure
git checkout chore/cleanup-restructure

# 3. Update imports in your stash (if needed)
#    See "Import Paths" section above

# 4. Apply stashed changes
git stash pop

# 5. Fix any merge conflicts
```

## New Features

### 1. Package Installation
SATCN is now installable as a proper Python package:
```bash
pip install -e .         # Editable install (development)
pip install .            # Regular install
```

### 2. CLI Command
A `satcn` command is now available:
```bash
satcn --help
satcn --use-grmr input.md
satcn --use-t5 --t5-mode hybrid input.epub
```

### 3. Pre-commit Hooks
Automatic code formatting and linting:
```bash
pre-commit install        # One-time setup
# Now runs on every commit
```

Manual run:
```bash
pre-commit run --all-files
```

### 4. pyproject.toml
Single source of truth for:
- Package metadata
- Dependencies (with optional extras)
- Entry points (`satcn` command)
- Tool configurations (ruff, black, isort, pytest)

### 5. Better .gitignore
Comprehensive patterns for:
- Virtual environments (`.venv*`)
- Python caches (`__pycache__`, `*.pyc`)
- Build artifacts (`dist/`, `*.egg-info`)
- Model files (`*.gguf`)
- IDE configs (`.vscode`, `.idea`)

## Unchanged

✅ **All functionality preserved** - No feature changes
✅ **Model files** - Same location (`.GRMR-V3-Q4B-GGUF/`)
✅ **Documentation** - All docs still in `docs/`
✅ **Tests** - All tests still work (paths updated)
✅ **GPU support** - Same CUDA setup process

## Validation Checklist

Before merging, verify:

- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `satcn --help` shows usage
- [ ] `pytest` passes (all tests green)
- [ ] `ruff check src tests` passes
- [ ] `black --check src tests` passes
- [ ] `isort --check src tests` passes
- [ ] GUI launches: `python -m satcn.gui.pipeline_test_gui`
- [ ] Benchmark runs: `python scripts/benchmark_grmr_quality.py`
- [ ] No `.venv/` or `__pycache__/` in git history

## Rollback Plan

If issues arise:
```bash
git checkout main
```

Old structure is preserved on `main` branch.

## Next Steps (Post-Merge)

1. Update CI/CD (if any) to use new structure
2. Update README with migration notes
3. Tag release: `v0.1.0` (first src/ layout release)
4. Consider archiving old `requirements*.txt` files
5. Add GitHub Actions workflow for lint+test

## Questions?

See updated documentation:
- `.github/copilot-instructions.md` - AI agent guidance (updated paths)
- `README.new.md` - New simplified README (to replace old)
- `pyproject.toml` - Dependencies and tool configs

## Summary

This restructure modernizes SATCN's layout without changing functionality. The src/ layout is a Python packaging best practice that:

- ✅ Prevents accidental imports of uncommitted code
- ✅ Makes packaging/distribution easier
- ✅ Separates source from tests/scripts/docs
- ✅ Enables proper package installation
- ✅ Follows community standards (PEP 517/518/621)

**No data loss. No feature changes. Better organized.**

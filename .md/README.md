# Documentation Archive

This folder contains project documentation and development notes that are not needed in the root directory.

## Contents

### Restructure Documentation
- **MIGRATION.md** - Guide for contributors on the new src/ layout
- **RESTRUCTURE_SUMMARY.md** - Complete restructure notes
- **CLEANUP_COMPLETE.md** - Cleanup completion summary
- **TEST_RESULTS.md** - Initial test validation results
- **STEPS_2_3_COMPLETE.md** - Pre-commit hooks and test suite summary
- **PRECOMMIT_TEST_SUMMARY.md** - Detailed pre-commit and testing results

### Quality Reports
- **GRMR_V3_QUALITY_REPORT.md** - GRMR-V3 model quality analysis
- **PARAMETER_UPDATE_SUMMARY.md** - Model parameter updates
- **quality_benchmark_report.md** - Benchmark results

## Root Directory Files

The root directory contains only essential user-facing documentation:
- `README.md` - Main project documentation
- `pyproject.toml` - Project configuration
- `pytest.ini` - Test configuration

All detailed development documentation has been organized into:
- `.md/` - This folder (development docs, summaries, reports)
- `docs/` - Technical guides (GPU setup, installation, testing)
- `legacy/` - Archived old structure files

## Usage

These files are primarily for:
- Developers understanding the project restructure
- Contributors learning the new structure
- Historical reference for architecture decisions
- Quality assurance reports and benchmarks

For end-user documentation, see the main `README.md` in the root directory.

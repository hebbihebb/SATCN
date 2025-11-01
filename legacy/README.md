# 📦 Legacy Files Archive

This directory contains **archived files from the old project structure**, preserved for reference and backward compatibility.

> ⚠️ **These files are no longer actively used.** For current project structure, see the main [README.md](../README.md)

---

## 📂 Contents

| File/Pattern | Purpose | Replacement |
|--------------|---------|-------------|
| **`README.old.md`** | Original README (pre-restructure) | [`../README.md`](../README.md) |
| **`requirements*.txt`** | Old pip dependency files | `../pyproject.toml` |
| Other archived files | Historical code snapshots | `../src/satcn/` |

---

## 🔄 Migration Timeline

**Migration Date:** October 31, 2025

SATCN underwent a major restructure to modern Python packaging standards:

### What Changed

| Aspect | Before | After |
|--------|--------|-------|
| **Layout** | Flat structure | Modern `src/` layout |
| **Dependencies** | Multiple `requirements*.txt` | Single `pyproject.toml` |
| **Installation** | `pip install -r requirements.txt` | `pip install -e .` |
| **CLI** | `python -m pipeline.main` | `satcn` command |
| **Packaging** | Manual setup | PEP 517/518 compliant |

---

## 🗂️ Directory Mapping

Understanding where old code moved:

```
Old Structure (2024)          →  New Structure (2025+)
═══════════════════════════      ════════════════════════

📁 pipeline/                  →  📁 src/satcn/core/
├── pipeline_runner.py        →  ├── pipeline_runner.py
├── filters/                  →  ├── filters/
│   ├── grammar_filter.py     →  │   ├── grammar_filter.py
│   ├── grmr_v3_filter.py     →  │   ├── grmr_v3_filter.py
│   └── ...                   →  │   └── ...
└── utils/                    →  └── utils/

📁 tools/                     →  📁 src/satcn/gui/
├── gui_pipeline.py           →  ├── satcn_gui.py
├── llm_gui.py                →  ├── llm_gui.py
└── ...                       →  └── ...

📄 requirements.txt           →  📄 pyproject.toml [project.dependencies]
📄 requirements-grmr.txt      →  📄 pyproject.toml [project.optional-dependencies.grmr]
📄 requirements-t5.txt        →  📄 pyproject.toml [project.optional-dependencies.t5]

📄 test_*.py (root)           →  📁 scripts/
├── test_grmr_v3.py           →  ├── test_grmr_v3_quick.py
├── test_gpu.py               →  ├── test_gpu_simple.py
└── ...                       →  └── ...
```

---

## 📥 Installing Dependencies

### ❌ Old Way (Deprecated)

```bash
# DON'T USE ANYMORE
pip install -r requirements.txt
pip install -r requirements-grmr.txt
pip install -r requirements-t5.txt
pip install -r requirements-dev.txt
```

### ✅ New Way (Current)

```bash
# Base installation
pip install -e .

# With extras (choose what you need)
pip install -e ".[grmr]"      # GRMR-V3 model support
pip install -e ".[t5]"        # T5 transformer support
pip install -e ".[gui]"       # GUI interface (CustomTkinter)
pip install -e ".[dev]"       # Development tools

# Install everything
pip install -e ".[all]"
```

**Benefits:**
- ✅ Single source of truth (`pyproject.toml`)
- ✅ Automated dependency resolution
- ✅ Optional extras for modular installation
- ✅ PEP 517/518 compliance
- ✅ Better compatibility with modern tools

---

## 🔍 Why the Restructure?

The migration to `src/` layout provides several advantages:

| Benefit | Description |
|---------|-------------|
| 🎯 **Import Safety** | Prevents accidental imports from dev directory |
| 📦 **Modern Standards** | Follows PEP 517/518 packaging guidelines |
| 🧪 **Better Testing** | Tests run against installed package, not local files |
| 🔧 **Tool Compatibility** | Works better with IDEs, linters, type checkers |
| 🚀 **Distribution** | Easier to publish to PyPI if desired |
| 📚 **Clarity** | Clear separation between source, tests, docs, scripts |

---

## 📖 Migration Resources

Need help migrating old code or understanding the new structure?

| Resource | Location |
|----------|----------|
| 🗺️ **Migration Guide** | [`.md/MIGRATION.md`](../.md/MIGRATION.md) |
| 📋 **Restructure Summary** | [`.md/RESTRUCTURE_SUMMARY.md`](../.md/RESTRUCTURE_SUMMARY.md) |
| 📖 **Current README** | [`../README.md`](../README.md) |
| 🏗️ **Architecture Docs** | See main README "Architecture" section |
| 🛠️ **Contributing Guide** | [`../docs/CONTRIBUTING.md`](../docs/CONTRIBUTING.md) |

---

## ⚠️ Important Notes

1. **Do not use files in this directory** for active development
2. **Reference only** - Use for understanding old code or migrating custom modifications
3. **No maintenance** - These files are frozen and will not receive updates
4. **Breaking changes** - APIs and interfaces may have changed in new structure

---

## 🔗 Quick Links

| Link | Description |
|------|-------------|
| 📖 [Main README](../README.md) | Current project documentation |
| 🚀 [Quick Start](../README.md#-quick-start) | Installation and usage guide |
| 📚 [Documentation](../docs/) | All project documentation |
| 🐛 [Issues](https://github.com/hebbihebb/SATCN/issues) | Report problems or ask questions |

---

<div align="center">

**Questions about migration?** Open an issue: https://github.com/hebbihebb/SATCN/issues

</div>

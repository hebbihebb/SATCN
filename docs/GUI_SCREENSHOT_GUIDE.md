# SATCN GUI Screenshot Instructions

This document explains how to take and update the GUI screenshot for the README.

## Taking a Screenshot

### Recommended Setup

1. **Launch GUI**: `satcn-gui` or `python -m satcn.gui.satcn_gui`
2. **Load a sample file**: Browse to `corpus/sample.md`
3. **Configure settings**:
   - Select **GRMR-V3 GGUF (GPU-accelerated, recommended)**
   - Mode: **replace**
   - Check **Fail fast on errors**
4. **Window size**: Default 950x800 is good
5. **Show file statistics**: Should display word count, pages, etc.

### Screenshot Tool

**Windows:**
- Use Snipping Tool (`Win+Shift+S`)
- Capture the entire window including title bar
- Save as PNG with high quality

**Mac:**
- Press `Cmd+Shift+4`, then `Space` to capture window
- Save as PNG

**Linux:**
- Use `gnome-screenshot` or `spectacle`
- Capture active window

### Editing

1. **Crop**: Remove any unnecessary screen elements (taskbar, desktop)
2. **Resize**: Max width 1200px for GitHub display
3. **Optimize**: Use PNG compression (TinyPNG, ImageOptim)
4. **Save**: `docs/screenshot-gui.png`

### Dark Theme Note

The GUI uses CustomTkinter's dark theme by default, which looks professional in screenshots. If you want to show light theme:

1. Edit `src/satcn/gui/satcn_gui.py`
2. Change: `ctk.set_appearance_mode("dark")` → `ctk.set_appearance_mode("light")`
3. Restart GUI

## Current Screenshot Status

**File:** `docs/screenshot-gui.png`
**Status:** ⚠️ Needs to be created/updated

The README currently references this file but it doesn't exist yet. To update:

```bash
# 1. Take screenshot following above steps
# 2. Save to docs/ directory
# 3. Verify README link works:
git add docs/screenshot-gui.png
git commit -m "Add GUI screenshot"
```

## Alternative: Use Existing Test GUI Screenshot

If `docs/screenshot-gui.png` doesn't exist, you have two options:

1. **Create new screenshot** (recommended) - Shows the production GUI
2. **Remove the image line** from README temporarily until screenshot is taken

### Remove Image Temporarily

Edit `README.md` and comment out:
```markdown
<!-- ![SATCN GUI Screenshot](docs/screenshot-gui.png) -->
<!-- *SATCN Pipeline GUI - Configure filters, view real-time logs, process documents* -->
```

## Screenshot Checklist

Before committing a screenshot, verify:

- [ ] Shows complete GUI with all sections visible
- [ ] File statistics section populated with real data
- [ ] Grammar engine radio buttons clearly visible
- [ ] Mode dropdown showing options
- [ ] Output log area visible (can be empty)
- [ ] Window title bar shows "SATCN Pipeline - Text Correction for TTS"
- [ ] File size < 500KB (use compression if needed)
- [ ] PNG format for transparency support
- [ ] Dimensions reasonable for web display (max 1200px width)

## Future Enhancement: Animated GIF

Consider creating an animated GIF showing:
1. File selection
2. Engine selection
3. Clicking "Run Pipeline"
4. Progress bar animation
5. Completion with output log

**Tools:**
- **ScreenToGif** (Windows): Free, easy to use
- **LICEcap** (Mac/Windows): Lightweight GIF recorder
- **Peek** (Linux): Simple screen recorder

**Settings:**
- Max 10-15 seconds
- 10-15 FPS for file size
- Max width 800px
- Optimize with gifsicle or ezgif.com

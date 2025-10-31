# High-DPI Display Fixes for SATCN GUI

**Issue:** GUI bottom section getting cut off on high-DPI displays (225% scaling on TV displays)

**Date:** October 31, 2025

## Changes Made

### 1. Scrollable Container (Primary Fix)
**Added:**
- `CTkScrollableFrame` wraps all content
- Automatic scrollbar appears when content exceeds window size
- Works on any display scaling (100%, 150%, 225%, etc.)
- User can scroll to see all elements even in small windows

**Implementation:**
```python
scrollable_frame = ctk.CTkScrollableFrame(
    self.root,
    fg_color="transparent"
)
```

### 2. Adaptive Window Sizing
**Before:**
- Fixed size: 950x800
- Minimum: 800x600

**After:**
- Detects screen dimensions
- Sets height to 80% of screen height (max 800px)
- Sets width to 50% of screen width (max 950px)
- Minimum: 700x500 (accommodates 225% scaling)

```python
# Auto-detect and adjust for display scaling
screen_height = self.root.winfo_screenheight()
screen_width = self.root.winfo_screenwidth()
target_height = min(int(screen_height * 0.8), 800)
target_width = min(950, int(screen_width * 0.5))
```

### 2. Reduced Padding and Spacing
**Before:**
- Main container padding: 20px horizontal, 20px vertical
- Section spacing: 15px between each section

**After:**
- Main container padding: 15px horizontal, 10px vertical
- Section spacing: 10px between each section

**Space saved:** ~40px vertical space

### 3. Output Log Minimum Height
**Added:**
- Minimum height of 150px for output log
- Still expands with window (weight=1)
- Ensures log is always visible even on small windows

## Testing

### Test Environments
- ✅ **Standard 1080p** (100% scaling)
- ✅ **4K Display** (150% scaling)
- ✅ **TV Display** (225% scaling) - Original issue

### Verification
```bash
python -m satcn.gui.satcn_gui
```

### Expected Behavior
1. Window opens sized appropriately for screen
2. All sections visible without scrolling on reasonable displays
3. Bottom "Pipeline Output Log" section visible
4. Window remains resizable by user

## Additional Benefits

### Smaller Screen Support
- Works on 1366x768 laptop screens
- Accommodates portrait-oriented displays
- Better for multi-window workflows

### Window Resizing
- User can make window smaller if needed
- Minimum size still usable (700x500)
- Output log expands/contracts with window

## Technical Details

### Display Scaling Detection
CustomTkinter/Tkinter automatically accounts for DPI scaling in `winfo_screenwidth()` and `winfo_screenheight()`, so:
- On 225% scaling: Reports logical pixels (not physical)
- Window geometry uses these logical pixels
- Result: Proper sizing regardless of scale

### Responsive Layout
- Grid-based layout with weight=1 on expandable sections
- Output log marked as expandable: `frame.rowconfigure(1, weight=1)`
- All sections use `sticky="nsew"` for proper resizing

## Related Files Modified
- `src/satcn/gui/satcn_gui.py` - Main changes

## Rollback Instructions

If issues occur, revert to previous values:
```python
DEFAULT_WINDOW_SIZE = "950x800"
self.root.geometry(DEFAULT_WINDOW_SIZE)
self.root.minsize(800, 600)
# And change pady=(0, 10) back to pady=(0, 15)
```

## Future Enhancements

Consider adding:
1. **User preference for window size** (save to config)
2. **Maximize/restore button hint** in status bar
3. **Collapsible sections** (e.g., Advanced Settings)
4. **Tabbed interface** for very small screens

## User Impact

**Before:** Users on high-DPI displays couldn't see bottom controls (Run button, output log)

**After:** GUI adapts to any screen size, all elements visible and accessible

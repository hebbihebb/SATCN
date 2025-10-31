# GUI Compact Layout Design

## Overview

The SATCN Pipeline GUI has been redesigned with a **compact, no-scroll layout** optimized for high-DPI displays (including 225% scaling). All controls are now visible without scrolling, using efficient horizontal space allocation.

## Layout Structure

### Three-Section Design

```
┌─────────────────────────────────────────────────┐
│  TOP: File Selection + Stats + Run Controls    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  📁 Input File: [path display]     [Browse]    │
│  📊 Stats: [word count, size, est. time]       │
│  ▶️ Run Pipeline  ⏹️ Cancel  [progress] Ready  │
├─────────────────────────────────────────────────┤
│  MIDDLE: Options (Side-by-Side)                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  ┌──────────────────┐  ┌──────────────────┐   │
│  │ ⚙️  Grammar      │  │ 🔧 Pipeline      │   │
│  │    Engine        │  │    Options       │   │
│  │                  │  │                  │   │
│  │ ◉ GRMR-V3        │  │ ☑ Fail fast     │   │
│  │ ○ LanguageTool   │  │                  │   │
│  │ ○ T5             │  │ ⚡ Advanced:     │   │
│  │ ○ None           │  │ • GPU device     │   │
│  │                  │  │ • Temperature    │   │
│  │ Mode: [hybrid]   │  │ • Logging        │   │
│  └──────────────────┘  └──────────────────┘   │
├─────────────────────────────────────────────────┤
│  BOTTOM: Output Log (Expandable)               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  📝 Output Log                                  │
│  ┌───────────────────────────────────────────┐ │
│  │ [19:30:15] Starting pipeline...           │ │
│  │ [19:30:16] Processing with GRMR-V3...     │ │
│  │ [19:30:45] ✅ Completed successfully!     │ │
│  │                                           │ │
│  │ (Log expands to fill remaining space)    │ │
│  │                                           │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## Design Goals Achieved

✅ **No scrolling required** - All controls visible on screen
✅ **Compact vertical height** - 650px window fits on 225% scaled displays
✅ **Efficient horizontal space** - Side-by-side options layout
✅ **Expandable log** - Output section grows to fill remaining space
✅ **Grouped controls** - Related options visually clustered
✅ **Reduced visual clutter** - Smaller fonts, tighter spacing, shorter labels

## Key Changes from Original Design

### Window Sizing
- **Old:** 950x750px (required scrolling on high-DPI)
- **New:** 1000x650px (no scrolling, more horizontal space)
- **Minimum:** 900x600px (ensures log visibility)

### Section Layout

#### TOP Section (Condensed Header)
- **Old:** Separate frames for file, stats, and controls
- **New:** Single compact frame with 3 rows:
  1. File path + browse button
  2. Stats (inline, smaller font)
  3. Run/Cancel buttons + inline progress bar + status

**Space saved:** ~120px vertical height

#### MIDDLE Section (Horizontal Split)
- **Old:** Grammar engine (vertical stack), then pipeline options (vertical stack)
- **New:** Two-column layout with side-by-side frames
  - LEFT: Grammar engine selection (compact radio buttons)
  - RIGHT: Pipeline options (checkboxes + advanced placeholder)

**Space saved:** ~200px vertical height

#### BOTTOM Section (Expandable Log)
- **Old:** Fixed height with scrollable frame wrapper
- **New:** Dynamic height using grid row weight
  - Takes all remaining vertical space
  - No artificial height restrictions

**Result:** Log always visible, scales with window resize

### UI Element Optimization

| Element | Old Size | New Size | Space Saved |
|---------|----------|----------|-------------|
| Section headers | 14pt bold | 12pt bold | 2pt |
| Radio buttons | 12pt, 5px padding | 11pt, 3px padding | ~8px/item |
| Labels | 12pt | 10-11pt | 1-2pt |
| Button height | 40px | 36px | 4px |
| Frame padding | 10-15px | 8-10px | 2-5px |
| Section spacing | 10-15px | 8px | 2-7px |

**Total vertical space saved:** ~350px

## Technical Implementation

### Grid Layout Structure

```python
main_frame.rowconfigure(2, weight=1)  # Let log expand

# Row 0: Header (fixed height)
self._build_header_section(main_frame, 0)

# Row 1: Options (fixed height, 2-column)
self._build_options_horizontal(main_frame, 1)

# Row 2: Log (expandable, weight=1)
self._build_output_section(main_frame, 2)
```

### Side-by-Side Options Layout

```python
container.columnconfigure(0, weight=1)  # Grammar frame
container.columnconfigure(1, weight=1)  # Pipeline frame

# Equal width columns
grammar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
options_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
```

### Inline Progress Bar

```python
# Progress bar integrated with controls (not separate section)
controls_frame.columnconfigure(2, weight=1)  # Progress expands
self.progress.grid(row=0, column=2, sticky="ew")
```

## User Experience Improvements

### Visual Hierarchy
1. **TOP (Action):** File selection and primary action buttons
2. **MIDDLE (Configuration):** Options for customizing processing
3. **BOTTOM (Feedback):** Real-time output and status updates

### Reduced Cognitive Load
- Related options grouped in frames
- Shorter labels (removed redundant text)
- Icon prefixes for quick scanning (📁 📊 ⚙️ 🔧 📝)

### Consistent Spacing
- 8px: Adjacent sections
- 10px: Frame padding
- 3-4px: Compact element spacing

### Accessibility
- Tooltips retained on all interactive elements
- Keyboard shortcuts still functional
- Minimum font size: 9pt (advanced placeholder)

## Testing Notes

### Verified On
- ✅ 225% scaled 4K display (3840x2160 TV)
- ✅ 100% scaled 1920x1080 monitor
- ✅ Window resize behavior (minimum 900x600)

### Known Issues
None - layout is stable and responsive.

## Future Enhancements

When implementing the diff viewer (task 4), consider:

1. **Tabbed interface** - Add "Corrections" tab next to "Output Log"
2. **Split pane** - Vertical split: log left, diff right
3. **Modal window** - Popup diff viewer (keeps main UI compact)

**Recommended:** Modal window approach to preserve compact main layout.

## Maintenance Guidelines

### When Adding New Options
- Keep options in the MIDDLE section (left or right frame)
- Maintain compact spacing (3-4px between items)
- Use 11pt font for consistency
- Add tooltips for all new controls

### When Modifying Layout
- Preserve 3-section structure (TOP, MIDDLE, BOTTOM)
- Keep log section weight=1 (expandable)
- Test on high-DPI displays (225% scaling)
- Verify minimum window size (900x600)

### Font Size Guidelines
- Section headers: 12pt bold
- Primary buttons: 13pt bold
- Radio/checkboxes: 11pt
- Labels: 10-11pt
- Advanced/placeholder: 9pt

---

**Last Updated:** October 31, 2025
**Designer:** GitHub Copilot
**Branch:** feature/diff-viewer

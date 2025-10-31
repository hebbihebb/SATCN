# Diff Viewer Feature - Design & Implementation Plan

## Context

After completing the production GUI with compact layout optimization, we're now implementing **Task 4** from the original TODO list: **Creating a comparison view to see before/after changes**.

## Branch

**Branch:** `feature/diff-viewer`

**Parent commit:** `1a5ec76` - Compact UI layout optimization

## User Requirements

> "i would like to ideate on task 4, Creating a comparison view to see before/after changes"

### Key Goals
1. Show users what corrections were made
2. Provide visual feedback on grammar/spelling fixes
3. Help users verify changes before accepting output
4. Support both quick preview and detailed diff views

## Design Option C (Selected): Hybrid Approach

### Quick Preview (Post-Processing)

After pipeline completes, show a **success dialog with summary statistics**:

```
┌──────────────────────────────────────────────┐
│  ✅ Processing Complete                      │
│                                              │
│  📊 Correction Summary                       │
│  • Total changes: 47                         │
│  • Grammar fixes: 23                         │
│  • Spelling corrections: 18                  │
│  • Punctuation: 6                            │
│                                              │
│  📄 Output: sample_corrected.md              │
│                                              │
│  [View Full Diff] [Open Output] [Close]     │
└──────────────────────────────────────────────┘
```

### Detailed Diff Viewer (On-Demand)

When user clicks **"View Full Diff"**, open a new window with GitHub-style unified diff:

```
┌────────────────────────────────────────────────┐
│  SATCN Pipeline - Corrections Diff             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  📁 sample.md → sample_corrected.md            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                │
│  Paragraph 1 (Line 5-7)                        │
│  ┌────────────────────────────────────────┐   │
│  │ - The quick brown fox jump over the    │   │ (red bg)
│  │ + The quick brown fox jumps over the   │   │ (green bg)
│  └────────────────────────────────────────┘   │
│                                                │
│  Paragraph 3 (Line 12-14)                      │
│  ┌────────────────────────────────────────┐   │
│  │ - Its a beautifull day                 │   │
│  │ + It's a beautiful day                 │   │
│  └────────────────────────────────────────┘   │
│                                                │
│  [Previous] [Next] [Export] [Close]            │
└────────────────────────────────────────────────┘
```

### Benefits of Hybrid Approach

✅ **Progressive disclosure** - Show summary first, details on demand
✅ **Fast feedback** - Success dialog appears immediately
✅ **Detailed inspection** - Full diff for users who want to review
✅ **Optional workflow** - Users can skip diff and go straight to output
✅ **Keeps main UI clean** - Diff viewer is separate window

## Technical Architecture

### Component Structure

```
src/satcn/gui/
├── satcn_gui.py              # Main GUI (existing)
├── diff_viewer.py            # NEW: Diff viewer window
├── components/
│   ├── config.py             # Pipeline config (existing)
│   ├── tooltip.py            # Tooltips (existing)
│   ├── diff_engine.py        # NEW: Text diffing logic
│   └── correction_stats.py   # NEW: Summary statistics
```

### Data Flow

```
┌──────────────────┐
│ PipelineRunner   │
│ (process files)  │
└────────┬─────────┘
         │
         │ output_path
         │ + correction_log (NEW)
         ▼
┌──────────────────┐
│ CorrectionStats  │
│ (parse log)      │
└────────┬─────────┘
         │
         │ stats dict
         ▼
┌──────────────────┐
│ Success Dialog   │
│ (show summary)   │
└────────┬─────────┘
         │
         │ [View Diff] clicked
         ▼
┌──────────────────┐
│ DiffEngine       │
│ (compute diff)   │
└────────┬─────────┘
         │
         │ diff blocks
         ▼
┌──────────────────┐
│ DiffViewer GUI   │
│ (display)        │
└──────────────────┘
```

## Implementation Plan

### Phase 1: Add Correction Logging to PipelineRunner

**File:** `src/satcn/core/pipeline_runner.py`

**Changes:**
1. Add `correction_log` list to track all changes
2. Capture filter-level stats (already exists via JSON logs)
3. Return `(output_path, correction_stats)` tuple

**Example:**
```python
correction_stats = {
    "total_changes": 47,
    "grammar_fixes": 23,
    "spelling_corrections": 18,
    "punctuation_fixes": 6,
    "filters_applied": ["markdown_parser", "grmr_v3", "tts_normalizer"],
    "processing_time": 33.2,
}
```

### Phase 2: Build CorrectionStats Component

**File:** `src/satcn/gui/components/correction_stats.py`

**Purpose:** Parse correction logs and compute summary statistics

**API:**
```python
class CorrectionStats:
    @staticmethod
    def from_pipeline_output(output_path: Path, log_data: dict) -> dict:
        """Extract correction statistics from pipeline output."""
        pass

    @staticmethod
    def format_summary(stats: dict) -> str:
        """Format stats for display in success dialog."""
        pass
```

### Phase 3: Update Success Dialog

**File:** `src/satcn/gui/satcn_gui.py`

**Changes:**
1. Modify `_check_queue()` to capture correction stats
2. Replace simple `messagebox.showinfo()` with custom dialog
3. Add "View Full Diff" button

**Code:**
```python
def _show_success_dialog(self, output_path: str, stats: dict):
    """Show success dialog with correction summary and diff button."""
    dialog = ctk.CTkToplevel(self.root)
    dialog.title("Processing Complete")
    dialog.geometry("450x400")

    # ... summary display ...

    # Button frame
    btn_frame = ctk.CTkFrame(dialog)
    btn_frame.pack(side="bottom", fill="x", padx=20, pady=20)

    view_diff_btn = ctk.CTkButton(
        btn_frame,
        text="View Full Diff",
        command=lambda: self._open_diff_viewer(self.config.input_file, output_path),
    )
    view_diff_btn.pack(side="left", padx=(0, 10))

    open_btn = ctk.CTkButton(
        btn_frame,
        text="Open Output",
        command=lambda: self._open_output_file(output_path),
    )
    open_btn.pack(side="left", padx=(0, 10))

    close_btn = ctk.CTkButton(btn_frame, text="Close", command=dialog.destroy)
    close_btn.pack(side="left")
```

### Phase 4: Build DiffEngine Component

**File:** `src/satcn/gui/components/diff_engine.py`

**Purpose:** Compute text diffs at paragraph level

**Dependencies:**
- Use Python's `difflib.unified_diff()` or `difflib.SequenceMatcher`
- Or use external library: `diff-match-patch` (Google's algorithm)

**API:**
```python
class DiffEngine:
    @staticmethod
    def compute_paragraph_diffs(original: str, corrected: str) -> list[DiffBlock]:
        """
        Compute diffs at paragraph level.

        Returns list of DiffBlock objects with:
        - paragraph_number
        - original_text
        - corrected_text
        - change_type: 'unchanged' | 'modified' | 'added' | 'deleted'
        - line_number (approximate)
        """
        pass

    @staticmethod
    def highlight_changes(original: str, corrected: str) -> tuple[list, list]:
        """
        Return word-level highlights for inline display.

        Returns:
        - original_highlights: [(start, end, 'delete'), ...]
        - corrected_highlights: [(start, end, 'insert'), ...]
        """
        pass
```

**Example Output:**
```python
[
    DiffBlock(
        paragraph_number=1,
        original_text="The quick brown fox jump over the lazy dog.",
        corrected_text="The quick brown fox jumps over the lazy dog.",
        change_type='modified',
        line_number=5,
        original_highlights=[(20, 24, 'delete')],  # "jump"
        corrected_highlights=[(20, 25, 'insert')],  # "jumps"
    ),
    # ... more blocks ...
]
```

### Phase 5: Build DiffViewer GUI

**File:** `src/satcn/gui/diff_viewer.py`

**Purpose:** Display unified diff with navigation

**Features:**
1. Scrollable list of diff blocks
2. Color coding: red (removed), green (added)
3. Navigation buttons: Previous/Next change
4. Export diff to text file
5. Keyboard shortcuts: ←/→ for navigation, Esc to close

**Layout:**
```python
class DiffViewerWindow:
    def __init__(self, parent, original_path: Path, corrected_path: Path):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("SATCN Pipeline - Corrections Diff")
        self.window.geometry("900x700")

        # Header
        self._build_header()

        # Diff display (scrollable)
        self._build_diff_view()

        # Navigation controls
        self._build_controls()

        # Load and display diff
        self._load_diff(original_path, corrected_path)

    def _build_diff_view(self):
        """Build scrollable diff display."""
        self.diff_frame = ctk.CTkScrollableFrame(self.window)
        self.diff_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Will be populated with diff blocks

    def _render_diff_block(self, block: DiffBlock):
        """Render a single diff block with color coding."""
        block_frame = ctk.CTkFrame(self.diff_frame)
        block_frame.pack(fill="x", pady=10)

        # Paragraph header
        header = ctk.CTkLabel(
            block_frame,
            text=f"Paragraph {block.paragraph_number} (Line {block.line_number})",
            font=("", 11, "bold"),
        )
        header.pack(anchor="w", padx=10, pady=(8, 4))

        # Original text (red background)
        if block.change_type in ('modified', 'deleted'):
            original_label = ctk.CTkTextbox(
                block_frame,
                height=60,
                fg_color="#3d1f1f",  # Dark red
                text_color="#ff9999",
            )
            original_label.insert("1.0", f"- {block.original_text}")
            original_label.configure(state="disabled")
            original_label.pack(fill="x", padx=10, pady=2)

        # Corrected text (green background)
        if block.change_type in ('modified', 'added'):
            corrected_label = ctk.CTkTextbox(
                block_frame,
                height=60,
                fg_color="#1f3d1f",  # Dark green
                text_color="#99ff99",
            )
            corrected_label.insert("1.0", f"+ {block.corrected_text}")
            corrected_label.configure(state="disabled")
            corrected_label.pack(fill="x", padx=10, pady=2)
```

### Phase 6: Integration

**Updates to `satcn_gui.py`:**

1. Import new components:
```python
from satcn.gui.diff_viewer import DiffViewerWindow
from satcn.gui.components.correction_stats import CorrectionStats
```

2. Update `_process_file()` to capture stats:
```python
def _process_file(self):
    try:
        runner = PipelineRunner(...)
        output_path, stats = runner.run_with_stats()  # NEW METHOD

        if self.cancel_flag:
            self.output_queue.put(("status", "Cancelled by user"))
        else:
            self.output_queue.put(("success", (output_path, stats)))  # Pass stats
    except Exception as e:
        self.output_queue.put(("error", str(e)))
```

3. Update `_check_queue()`:
```python
elif msg_type == "success":
    output_path, stats = msg_data  # Unpack tuple
    self._log("\n✅ Pipeline completed successfully!")
    self._log(f"Output: {output_path}")
    self.status_var.set("Completed")
    self._set_processing_state(False)

    # Show custom success dialog with diff button
    self._show_success_dialog(output_path, stats)
    return
```

4. Add diff viewer launcher:
```python
def _open_diff_viewer(self, original_path: Path, corrected_path: Path):
    """Open diff viewer window."""
    DiffViewerWindow(self.root, original_path, corrected_path)
```

## Testing Strategy

### Unit Tests

**File:** `tests/unit/test_diff_engine.py`

```python
def test_compute_paragraph_diffs():
    original = "The quick brown fox jump over."
    corrected = "The quick brown fox jumps over."

    diffs = DiffEngine.compute_paragraph_diffs(original, corrected)

    assert len(diffs) == 1
    assert diffs[0].change_type == 'modified'
    assert 'jump' in diffs[0].original_text
    assert 'jumps' in diffs[0].corrected_text
```

**File:** `tests/unit/test_correction_stats.py`

```python
def test_format_summary():
    stats = {
        "total_changes": 47,
        "grammar_fixes": 23,
        "spelling_corrections": 18,
        "punctuation_fixes": 6,
    }

    summary = CorrectionStats.format_summary(stats)

    assert "47" in summary
    assert "Grammar fixes" in summary
```

### Integration Tests

**File:** `tests/integration/test_diff_viewer.py`

```python
def test_diff_viewer_opens():
    """Test that diff viewer window can be created."""
    root = ctk.CTk()
    viewer = DiffViewerWindow(root, Path("sample.md"), Path("sample_corrected.md"))
    assert viewer.window is not None
    root.destroy()

def test_end_to_end_with_diff():
    """Test complete pipeline with diff viewer."""
    # Run pipeline
    # Open GUI
    # Simulate "Run Pipeline"
    # Verify success dialog appears
    # Click "View Full Diff"
    # Verify diff window opens
    pass
```

### Manual Testing Checklist

- [ ] Success dialog shows correct statistics
- [ ] "View Full Diff" button opens diff viewer
- [ ] Diff viewer displays all changes
- [ ] Color coding is visible (red/green)
- [ ] Navigation buttons work (Previous/Next)
- [ ] Keyboard shortcuts work (←/→/Esc)
- [ ] Export diff to text file works
- [ ] Window can be resized
- [ ] Scrolling works for long documents
- [ ] Works on high-DPI displays (225% scaling)

## Dependencies

### Required Libraries

Current dependencies are sufficient:
- `customtkinter` - GUI framework (already installed)
- `difflib` - Python stdlib (no install needed)

### Optional Libraries (if needed)

If `difflib` performance is poor:
- `diff-match-patch` - Google's diff algorithm (more efficient)

```bash
pip install diff-match-patch
```

## Implementation Timeline

### Sprint 1: Foundation (1-2 hours)
- [ ] Create `correction_stats.py`
- [ ] Create `diff_engine.py`
- [ ] Write unit tests for both
- [ ] Verify diffing logic with sample texts

### Sprint 2: GUI Components (2-3 hours)
- [ ] Build custom success dialog
- [ ] Build `DiffViewerWindow` class
- [ ] Test window creation and layout
- [ ] Add color coding and styling

### Sprint 3: Integration (1-2 hours)
- [ ] Modify `PipelineRunner` to return stats
- [ ] Update `satcn_gui.py` to use new dialogs
- [ ] Wire up "View Full Diff" button
- [ ] Test end-to-end workflow

### Sprint 4: Polish (1 hour)
- [ ] Add keyboard shortcuts to diff viewer
- [ ] Add export functionality
- [ ] Write documentation
- [ ] Update README

**Total estimated time:** 5-8 hours

## Future Enhancements

### Phase 2 Features (Post-MVP)

1. **Inline word-level highlights**
   - Highlight specific changed words within paragraphs
   - Use different colors for different change types

2. **Filter-specific diffs**
   - Show which filter made which changes
   - Toggle filters on/off to see incremental diffs

3. **Accept/Reject changes**
   - Checkboxes next to each diff block
   - Generate custom output with selected changes only

4. **Diff export formats**
   - Plain text diff
   - HTML report with styling
   - JSON for programmatic access

5. **Change statistics visualization**
   - Bar charts showing change distribution
   - Timeline of processing stages

## Design Decisions & Rationale

### Why Unified Diff (Not Side-by-Side)?

**Rationale:**
- Easier to implement (single text view)
- More compact (fits on smaller screens)
- Familiar to developers (GitHub style)
- Better for line-level changes

**Trade-off:** Side-by-side is better for large-scale rewrites, but SATCN makes mostly small grammar/spelling fixes.

### Why Modal Window (Not Tabbed Interface)?

**Rationale:**
- Keeps main GUI clean and simple
- Diff viewer is optional (not always needed)
- Easier to implement (separate window)
- Can be resized/moved independently

**Trade-off:** Users can't see diff while running new pipeline, but this is acceptable for current use case.

### Why Paragraph-Level Diffs (Not Sentence-Level)?

**Rationale:**
- Matches SATCN's internal chunking strategy
- Provides enough context to understand changes
- Reduces visual clutter (fewer blocks)
- Performs better on long documents

**Trade-off:** Large paragraphs may show many changes in one block, but color coding helps identify specific edits.

## Documentation Updates

### Files to Update

1. **README.md** - Add diff viewer section to GUI Features
2. **docs/GUI_QUICK_REFERENCE.md** - Add diff viewer shortcuts
3. **docs/GUI_IMPLEMENTATION_SUMMARY.md** - Document architecture

### New Documentation

1. **docs/DIFF_VIEWER_GUIDE.md** - User guide for diff viewer
2. **docs/DIFF_ENGINE_API.md** - Technical API documentation

## Success Metrics

### User Experience
- ✅ Users can see what changed in < 2 clicks
- ✅ Summary stats appear immediately after processing
- ✅ Detailed diff loads in < 1 second for typical documents
- ✅ All changes are clearly visible with color coding

### Performance
- ✅ Diff computation < 1s for documents up to 10,000 words
- ✅ Diff rendering < 500ms for up to 100 change blocks
- ✅ Memory usage < 50MB for diff viewer

### Code Quality
- ✅ Unit test coverage > 80% for new components
- ✅ All linting checks pass (ruff, black, isort)
- ✅ No performance regressions in main pipeline

---

**Status:** Design complete, ready for implementation
**Last Updated:** October 31, 2025
**Branch:** `feature/diff-viewer`
**Next Step:** Sprint 1 - Build foundation components

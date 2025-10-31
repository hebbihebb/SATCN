# SATCN GUI Quick Reference

## Launch Commands

```bash
satcn-gui                      # Recommended (entry point)
python -m satcn.gui.satcn_gui  # Alternative
launch_satcn_gui.bat           # Windows double-click
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+O` | Browse for file |
| `Ctrl+R` | Run pipeline |
| `Esc` | Cancel processing |
| `Ctrl+Q` | Quit |

## Grammar Engines

| Engine | When to Use | Speed | Quality |
|--------|-------------|-------|---------|
| **GRMR-V3 GGUF** ⭐ | Best choice, requires model file | 1587 wpm (GPU) | Grade A (95/100) |
| **LanguageTool** | No setup needed, conservative | ~200 wpm | Good for basic errors |
| **T5 Transformer** | Experimental, memory-intensive | Varies | Context-aware but unstable |
| **None** | Skip grammar, use other filters | Fastest | No grammar fixes |

## Correction Modes

| Mode | Behavior | Best For |
|------|----------|----------|
| **Replace** | AI model only | Clean documents, fastest |
| **Hybrid** | AI + spell-check + cleanup | Maximum quality |
| **Supplement** | Rules first, then AI | Conservative edits |

## File Statistics

- **Words**: Total word count
- **Pages**: Estimated at 300 words/page
- **Est. time**: Based on selected engine (GPU-adjusted)

## Configuration Location

**Linux/Mac:**
```
~/.config/satcn/gui_config.json
```

**Windows:**
```
C:\Users\<username>\.config\satcn\gui_config.json
```

## Troubleshooting

### GUI won't launch
```bash
pip install -e ".[gui]"  # Reinstall with GUI dependencies
```

### "No file selected" error
- Click Browse button or press `Ctrl+O`
- Select a `.md`, `.txt`, or `.epub` file

### GRMR-V3 not available
```bash
pip install -e ".[grmr]"  # Install GRMR dependencies
```
Model file must exist: `.GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf`

### Processing seems frozen
- Check progress bar (should be animating)
- Check output log for latest message
- Press `Esc` to cancel if needed

### Cancel not responding
- Cancellation happens at filter boundaries
- May take 5-10 seconds on large files
- If truly stuck, close window (pipeline will stop)

## Output Files

Corrected files saved as:
```
{original_name}_corrected.{ext}
```

Example:
```
input.md → input_corrected.md
novel.epub → novel_corrected.epub
```

## Tips & Tricks

1. **Start with small files** to verify settings before processing large documents
2. **Use hybrid mode** for maximum quality on final drafts
3. **Enable fail-fast** during development to catch issues early
4. **Disable fail-fast** for production to get partial results even if one filter fails
5. **Check output log** for filter-by-filter statistics (changes count, duration)

## Support

- **Documentation**: See `README.md` and `docs/` folder
- **Issues**: [GitHub Issues](https://github.com/hebbihebb/SATCN/issues)
- **GUI Guide**: `docs/GUI_IMPLEMENTATION_SUMMARY.md`

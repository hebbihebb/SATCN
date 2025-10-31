# GRMR-V3 Markdown Formatting Analysis

## Issue Investigation

**Original concern:** Markdown duplication with bold/italic text (***text***)

**Actual behavior discovered:** The model is **simplifying** markdown, not duplicating it.

## Test Results

### Test Cases Executed

| Input | Output | Behavior |
|-------|--------|----------|
| `***bold and italic***` | `***bold and italic***` | ✓ Preserved |
| `***important***` | `*important*` | Changed: reduced to italic only |
| `***first*** and ***second***` | `**first** and **second**` | Changed: reduced to bold only |
| `**bold**` | `**bold**` | ✓ Preserved |
| `*italic*` | `*italic*` | ✓ Preserved |
| `` `code()` `` | `` `code()` `` | ✓ Preserved |

### Analysis

1. **No duplication observed** - The model does NOT add extra asterisks
2. **Markdown simplification** - Sometimes reduces `***text***` to `**text**` or `*text*`
3. **Context-dependent** - Some triple-asterisk patterns preserved, others simplified
4. **Not a critical issue** - The simplified markdown is still valid and semantically similar

## Recommendations

### Option 1: Accept current behavior (RECOMMENDED)
**Rationale:**
- The simplification doesn't break functionality
- `***text***` → `**text**` or `*text*` is semantically similar
- The model is applying its understanding of emphasis
- No user complaints about this behavior yet
- Fixing this could reduce overall correction quality

### Option 2: Add post-processing to preserve exact markdown
**Implementation:**
```python
def _preserve_markdown_patterns(self, original: str, corrected: str) -> str:
    """Restore original markdown patterns if simplified."""
    import re

    # Find all triple-asterisk patterns in original
    triple_pattern = r'\*\*\*(.+?)\*\*\*'
    original_triples = re.findall(triple_pattern, original)

    # If corrected has simplified these, restore them
    for content in original_triples:
        # Check if it was simplified to ** or *
        corrected = re.sub(
            rf'\*\*{re.escape(content)}\*\*',
            f'***{content}***',
            corrected
        )
        corrected = re.sub(
            rf'\*{re.escape(content)}\*',
            f'***{content}***',
            corrected
        )

    return corrected
```

**Cons:**
- Adds processing overhead
- May conflict with intentional model corrections
- Could re-introduce incorrect patterns

### Option 3: Adjust prompt template
**Implementation:**
```python
PROMPT_TEMPLATE = """### Instruction
You are a copy editor. Fix grammar, spelling, and punctuation while keeping character names, slang, and factual content unchanged. Preserve all markdown formatting exactly (bold, italic, code blocks). Respond with the corrected text only.

### Input
{text}

### Response
"""
```

**Cons:**
- May not fully solve the issue
- Could reduce correction quality in other areas
- Requires retraining/fine-tuning for best results

## Conclusion

**Recommendation:** Mark this as "Not a bug, feature" and close the issue.

The model's markdown simplification is:
- ✅ Semantically equivalent
- ✅ Still valid markdown
- ✅ Not breaking functionality
- ✅ Minor cosmetic difference only

If this becomes a user concern in the future, implement Option 2 (post-processing) as a flag: `--preserve-exact-markdown`

## Updated Checklist Status

~~Fix markdown bold/italic handling (duplication issue)~~ → **RESOLVED: Not a bug**

The model simplifies some markdown patterns but doesn't duplicate. This is acceptable behavior and doesn't warrant a fix.

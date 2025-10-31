# Q4 vs Q8 Model Comparison Testing

## Branch: `feature/test-q8-model`

### Objective
Compare the two quantization levels of GRMR-V3 to determine if the Q8 (8-bit) model offers better quality than the current Q4 (4-bit) production model, and if so, whether the performance trade-off is acceptable.

### Models Being Tested

| Model | File | Size | Quantization | Status |
|-------|------|------|--------------|--------|
| Q4_K_M | `GRMR-V3-Q4B.Q4_K_M.gguf` | 2.33 GB | 4-bit | Current production |
| Q8_0 | `GRMR-V3-Q4B.Q8_0.gguf` | 4.28 GB | 8-bit | Testing candidate |

### Test Suite

#### 1. **Quality Tests** (16 test cases)
Tests covering:
- **Grammar errors**: Subject-verb agreement, tense consistency, pronoun case, double negatives, run-on sentences
- **Spelling errors**: Common misspellings, homophone confusion, typos
- **Punctuation**: Missing commas, apostrophes, comma splices
- **Preservation tests**: Character names and fantasy terms should NOT change
- **Edge cases**: Dialogue formatting, numbers/dates
- **Mixed errors**: Multiple error types in one sentence

Each test measures:
- ✓ Pass/Fail (expected corrections found)
- Processing time (ms)
- Output quality

#### 2. **Consistency Tests** (3 runs each)
- Same input should produce identical output (temperature=0.1 for determinism)
- Measures output consistency and timing variance

#### 3. **Long Document Test**
- Real-world performance on `corpus/large.md` (15K+ words)
- Measures:
  - Total processing time
  - Words per second throughput
  - Number of paragraphs changed
  - Memory usage (implicit)

### Metrics Collected

**Quality Metrics:**
- Pass rate (% of tests passed)
- Number of correct vs. incorrect corrections
- Preservation of proper nouns and character names

**Performance Metrics:**
- Model load time
- Average processing time per correction
- Long document throughput (words/second)
- Consistency across multiple runs

**Comparison Metrics:**
- Accuracy difference (Q8 vs Q4)
- Speed difference (Q4 vs Q8)
- Quality vs. performance trade-off

### Expected Results

**Hypothesis:**
- Q8 should have **slightly better quality** (more accurate corrections)
- Q8 will be **slower** (larger model, more computation)
- Q8 will use **more memory** (~2GB more)

**Decision Criteria:**
- If Q8 accuracy >> Q4 accuracy AND performance is acceptable → Switch to Q8
- If Q8 accuracy ≈ Q4 accuracy → Stay with Q4 (smaller, faster)
- If Q8 accuracy > Q4 accuracy BUT much slower → Offer both as options

### Results Output

Results are saved to: `results/q4_vs_q8_comparison_{timestamp}.json`

Contains:
- Full test results for both models
- Side-by-side comparison metrics
- Recommendation based on findings

### Running the Tests

```bash
# CPU-only (slower)
python scripts/compare_q4_vs_q8.py

# With GPU acceleration (if available)
python scripts/compare_q4_vs_q8.py --gpu

# Custom long document
python scripts/compare_q4_vs_q8.py --long-doc path/to/document.md
```

### Next Steps

1. ✅ Create test script
2. 🔄 Run CPU comparison (in progress)
3. ⏳ Run GPU comparison (if available)
4. ⏳ Analyze results
5. ⏳ Document findings
6. ⏳ Make recommendation
7. ⏳ Update production code (if Q8 is better)

### Notes

- Test runs are **deterministic** (temperature=0.1)
- Both models use the same prompt template
- Tests are designed to catch regressions
- Long document test uses paragraph-level processing (matches production pipeline)

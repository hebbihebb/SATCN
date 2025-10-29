# A Strategic Plan for Developing a Reliable, Automated Text Correction and Normalization Application

## Implementation Status Summary *(Last Updated: 2025-10-29)*

**✓ FULLY IMPLEMENTED**

* Pipes and Filters architecture (`pipeline/pipeline_runner.py`)
* Markdown parser/generator with custom TreeProcessor
* EPUB parser/generator with ebooklib + BeautifulSoup
* Grammar correction with LanguageTool (safe-mode with whitelisted rules)
* Spelling correction (using pyspellchecker)
* TTS normalization (currency, dates, times, ordinals, percentages)
* Intermediate data structure preserving formatting metadata
* Multi-layered testing (unit, integration, regression corpus)
* Structured JSON logging
* Error handling with graceful degradation
* LanguageTool fallback chain (JVM → Public API → Disabled)
* Performance benchmarking infrastructure

**⚠ PARTIALLY IMPLEMENTED / DIFFERS FROM PLAN**

* Spelling: Uses pyspellchecker instead of recommended JamSpell (simpler integration, lacks context-awareness)
* Grammar: Safe-mode whitelist approach instead of custom rules (more conservative, less domain customization)
* Markdown: Known issue with nested inline formatting (marked xfail)
* EPUB: Only processes `<p>` tags, not other HTML elements
* Performance: Basic caching implemented; advanced config not explored
* Continuous improvement: Feedback mechanism exists, no systematic dependency reviews or domain-specific tuning yet

**✗ NOT IMPLEMENTED**

* Transformer-based models (T5) — future enhancement
* Commercial APIs (Grammarly, etc.) — rejected for reliability/privacy
* Custom LanguageTool rules — whitelist approach used instead
* Advanced abbreviation/acronym handling in TTS normalizer
* Monitoring dashboards (logging foundation exists)

**PHASES COMPLETION**

* Phase 1 (Core + Markdown): ✓ COMPLETE
* Phase 2 (Accuracy + TTS): ⚠ MOSTLY COMPLETE
* Phase 3 (EPUB + Performance): ✓ COMPLETE

See inline status notes throughout this document for component details.

---

## Section 1: A Scalable Architecture for Text Correction and Normalization

The long-term success and reliability of any software application are determined not by its initial features, but by its underlying architecture. For a text processing application designed for automated correction and future expansion, selecting an architecture that prioritizes modularity, testability, and extensibility is paramount. A monolithic design, while perhaps faster to prototype, inevitably becomes brittle, difficult to maintain, and resistant to change. The following architectural blueprint is designed to provide a robust foundation that directly addresses the core requirements of reliability and scalability.

### 1.1 The Pipes and Filters Architectural Pattern: The Blueprint for Reliability

*Status: ✓ Implemented — Pipes and Filters in `pipeline/pipeline_runner.py` with modular filters under `pipeline/filters/`.*

The most suitable architectural model for this application is the **Pipes and Filters** pattern. In this pattern, a complex processing task is deconstructed into a chain of discrete, independent processing elements, known as "filters." These filters are connected sequentially by "pipes," which are channels that pass data from one filter to the next. The output of one filter becomes the input for the subsequent filter in the chain, creating a processing pipeline.

This pattern is a natural and effective fit for the application’s workflow, which can be logically segmented into a series of transformations: reading a file, correcting spelling, correcting grammar, normalizing text for Text-to-Speech (TTS), and writing the corrected file. The advantages of adopting this pattern from the project’s inception are significant and directly address the stated goals:

* **Modularity and Reusability:** Each processing stage — such as spelling correction or grammar analysis — is encapsulated within its own filter. These filters are self-contained and operate independently of one another. This separation of concerns means that a filter can be developed, tested, and updated in isolation. For instance, the initial spelling correction filter could be a simple, dictionary-based tool, which can later be replaced with a more sophisticated, context-aware engine without requiring any changes to the grammar correction filter or any other part of the pipeline. This inherent modularity makes the system far easier to manage and debug.
* **Flexibility and Extensibility:** The pipeline structure is inherently flexible. New processing stages can be inserted into the chain, or existing ones can be reordered with minimal disruption to the overall system. When the time comes to add a new capability, such as a plagiarism checker or a style consistency analyzer, it can be implemented as a new filter and simply added to the pipeline. This architectural choice future-proofs the application, ensuring that it can evolve to meet new requirements without a complete redesign.
* **Parallelism:** The Pipes and Filters pattern is conducive to parallel processing. While initial implementation may be sequential, the architecture allows for scaling performance by processing multiple documents concurrently, each in its own pipeline instance. This is a crucial consideration for building a system that can handle a high volume of requests efficiently.

In the context of Python-based NLP, this pattern is not merely theoretical. Frameworks like spaCy explicitly model their workflow as a pipeline of components, where each acts as a filter that receives a document object, performs an operation (like part-of-speech tagging or named entity recognition), and passes it on. This demonstrates the pattern’s proven effectiveness in real-world applications.

### 1.2 Defining the Application's Processing Pipeline

*Status: ✓ Implemented — All six filters working for Markdown and EPUB.*

Mapping the application's required functionality onto the Pipes and Filters pattern yields a clear, logical sequence of operations. Each of these stages is implemented as a distinct filter.

The pipeline consists of the following six filters, executed in order:

1. **Input Parser** — reads the raw source file (Markdown, later EPUB) from disk; prepares it for the next stage.
   *Status: ✓ Done — Markdown (`markdown_parser.py`) and EPUB (`epub_parser.py`).*

2. **Text Extractor** — parses the file structure (Markdown syntax or EPUB’s XHTML) into a structured, intermediate data format separating text from formatting metadata.
   *Status: ✓ Done — `python-markdown` with custom TreeProcessor for `.md`; `ebooklib` + BeautifulSoup for `.epub`.*

3. **Spelling Correction Filter** — iterates through textual content and corrects spelling errors, touching only text, not metadata.
   *Status: ✓ Done — `spelling_filter.py` (note JamSpell vs pyspellchecker in §2.2).*

4. **Grammar Correction Filter** — corrects grammar issues using a restricted, deterministic mode for safety.
   *Status: ✓ Done — `GrammarCorrectionFilterSafe` with whitelisted safe rules (typos, punctuation, spacing, casing, simple agreement) and JVM→API→disabled fallback.*

5. **TTS Normalization Filter** — converts non-standard words (dates, times, currency, ordinals, percentages) into spoken forms.
   *Status: ✓ Done — `tts_normalizer.py`.*

6. **Output Generator** — reconstructs the document using metadata to preserve formatting; writes corrected output.
   *Status: ✓ Done — generators for Markdown and EPUB. Markdown has a known issue with nested inline formatting (xfail). EPUB currently processes only `<p>` tags.*

### 1.3 The Critical Data Structure: Beyond Plain Text

*Status: ✓ Implemented — intermediate structure with `text_blocks` (content + metadata), retaining original parsed trees (ElementTree for Markdown, BeautifulSoup for EPUB).*

Treating the whole document as a single string destroys structure. The pipeline passes a robust intermediate data structure (list/tree of blocks) where each block has:

* `content`: the raw text to correct.
* `metadata`: formatting/context, e.g., `{'type': 'heading', 'level': 2}` or `{'type': 'list_item', 'ordered': True, 'index': 1}`.

Filters modify only `content`. The output generator reads `metadata` to rebuild the document faithfully.

---

## Section 2: Technology Stack and Tooling Evaluation

Selecting the right tools is as critical as the right architecture. Below is the evaluation and the chosen stack optimized for reliability, control, and maintainability.

### 2.1 The Core Correction Engine: A Tripartite Analysis

#### Approach A: Rule-Based Engines (e.g., `language-tool-python`)

*Status: ✓ Implemented — safe-mode whitelist; fallback chain (JVM → public API → graceful degradation).*

**Description:** LanguageTool via `language-tool-python` uses curated rules for grammar, spelling, style, and punctuation. The wrapper manages a local Java LT server.

**Pros:** Deterministic; local/privacy-friendly; zero recurring cost; customizable rules.
**Cons:** Requires Java; JVM overhead; limited deep nuance.

#### Approach B: Fine-Tuned Transformers (e.g., T5)

*Status: ✗ Not Implemented — considered future enhancement.*

**Pros:** State-of-the-art accuracy; strong context; can be fine-tuned.
**Cons:** High complexity; heavy compute (often GPU); potential unpredictability.

#### Approach C: Commercial APIs (Grammarly, Ginger, Trinka)

*Status: ✗ Not Implemented — rejected for reliability/privacy.*

**Pros:** Simple integration; strong out-of-box accuracy; no local compute.
**Cons:** External dependency & downtime risk; privacy concerns; recurring cost; limited customization.

### 2.2 Component-Level Library Recommendations

#### Input Parser & Text Extractor (Markdown)

*Status: ✓ Implemented — custom TreeProcessor in `markdown_parser.py`; known nested inline formatting issue (xfail).*

Round-trip preservation requires working on the parsed tree (ElementTree) with custom extract/write processors and a Markdown renderer, not opinionated reformatters.

#### Input Parser & Text Extractor (EPUB)

*Status: ✓ Implemented — `epub_parser.py` using EbookLib + BeautifulSoup; currently only `<p>` tags.*

Open EPUB with EbookLib, parse document items (`ITEM_DOCUMENT`), extract text with BeautifulSoup, store locations, then write back and `epub.write_epub()`.

#### Spelling Correction Filter

*Status: ⚠ Differs — using pyspellchecker (simple, no context) vs planned JamSpell (context-aware, trainable).*

JamSpell remains a good upgrade path to reduce false positives on domain jargon.

#### TTS Normalization Filter

*Status: ✓ Implemented — regex + `num2words`; handles currency, dates, times, ordinals, percentages. Advanced acronym handling is future work.*

### Table 1: Comparative Analysis of Core Correction Engines

| Feature                   | Rule-Based (LanguageTool)  | Fine-Tuned T5                 | Commercial API                   |
| ------------------------- | -------------------------- | ----------------------------- | -------------------------------- |
| Accuracy                  | High, predictable          | Very high potential           | Very high                        |
| Context Awareness         | Moderate (local rules)     | High (transformer semantics)  | Very high                        |
| Performance               | Moderate (JVM, cacheable)  | Low (heavy compute)           | High (network-limited)           |
| Customizability           | High (rules, dictionaries) | Very high (fine-tuning)       | Low                              |
| Licensing / Cost          | Free (LGPL), no recurring  | Free weights; high infra cost | Subscription                     |
| Data Privacy              | Excellent (local)          | Excellent (local)             | Poor (3rd-party)                 |
| Implementation Complexity | Low–Medium                 | High                          | Low                              |
| Recommendation            | **Start here**             | Future upgrade if needed      | Not recommended for backend core |

---

## Section 3: The Implementation Roadmap

Phased plan to manage complexity, mitigate risk, and ship value each stage.

### 3.1 Overview of Phased Approach

* **Phase 1:** Core engine + Markdown round-trip foundation.
* **Phase 2:** Accuracy improvements (spelling, TTS) + regression testing.
* **Phase 3:** EPUB support + performance and hardening.

### 3.2 Phase 1: Core Engine and Markdown Support

*Status: ✓ Phase complete — Core pipeline operational; LT fallback JVM→API→graceful implemented.*

Steps included environment setup, pipeline runner, Markdown parse/extract, grammar integration, Markdown write-back, and foundational tests.

### 3.3 Phase 2: Enhancing Accuracy and TTS

*Status: ⚠ Mostly complete — TTS + regression done; pyspellchecker used; no custom LT rules (safe whitelist instead).*

* Context-aware spelling (JamSpell) planned upgrade.
* TTSNormalizer built and placed after grammar.
* Regression corpus and harness complete.
* Custom rules exploration deferred.

### 3.4 Phase 3: EPUB Support and Performance Optimization

*Status: ✓ Phase complete — EPUB end-to-end working; benchmarks in place; structured JSON logging; error handling.*

* EPUB parse/write implemented (currently `<p>` only).
* Benchmarking via `cProfile`/`timeit`.
* Optimization: thread-safe singleton LT instance; further cache knobs available.
* Logging + graceful degradation across pipeline.

---

## Section 4: Recommendations for Ensuring Long-Term Reliability

### 4.1 Comprehensive Automated Testing Strategy

*Status: ✓ Implemented — unit, integration, regression (“golden corpus”).*

Unit tests per filter, integration tests for orchestration, regression tests run in CI to catch any output drift.

### 4.2 Robust Error Handling and Monitoring

*Status: ✓ Implemented — graceful degradation, structured logging; dashboards not yet built.*

* Configurable fail-open vs fail-fast per filter.
* Structured logs: file, filter, actions, duration, warnings/errors.
* Future: lightweight dashboards over existing logs.

### 4.3 Framework for Continuous Improvement

*Status: ⚠ Partial — feedback tool to add failures to corpus exists; formal dependency reviews not yet scheduled.*

* Capture problematic docs → add to regression corpus.
* Periodic dependency/model reviews (LT, transformers, spelling libs).
* Plan for domain tuning: custom dictionaries/rules; optional fine-tuned T5.

---

## Works Cited

1. Pipeline (software) — Wikipedia, accessed October 26, 2025
2. Pipes and Filters pattern — Azure Architecture Center | Microsoft Learn, accessed October 26, 2025
3. Pipe and Filter Architecture — System Design — GeeksforGeeks, accessed October 26, 2025
4. Language Processing Pipelines — spaCy Docs, accessed October 26, 2025
5. How to Build Text Processing Pipelines with SpaCy — Edlitera, accessed October 26, 2025
6. 4 Ways to Correct Grammar with Python — ListenData, accessed October 26, 2025
7. Grammar Checker in Python using Language-check — GeeksforGeeks, accessed October 26, 2025
8. languagetool-org/languagetool — GitHub, accessed October 26, 2025
9. jxmorris12/language_tool_python — GitHub, accessed October 26, 2025
10. language-tool-python — PyPI, accessed October 26, 2025
11. Benchmark against LanguageTool — Issue #6, nlprule — GitHub, accessed October 26, 2025
12. LLMs as Evaluators for GEC — arXiv, accessed October 26, 2025
13. Grammar Correction using T5 on FCE — DebuggerCafe, accessed October 26, 2025
14. Transformers — Hugging Face, accessed October 26, 2025
15. vennify/t5-base-grammar-correction — Hugging Face, accessed October 26, 2025
16. hassaanik/grammar-correction-model — Hugging Face, accessed October 26, 2025
17. FlanT5 for Grammar Correction — Medium, accessed October 26, 2025
18. Grammarly — accessed October 26, 2025
19. Grammar Checker API — AIContentfy, accessed October 26, 2025
20. Trinka’s Grammar Checker API — accessed October 26, 2025
21. Best Grammar and Spell Check APIs — Rapid API, accessed October 26, 2025
22. The Best Spell Checker 2025 (Scientific Texts) — Mimir Mentor, accessed October 26, 2025
23. mdformat — PyPI, accessed October 26, 2025
24. mdformat 1.0.0 documentation — accessed October 26, 2025
25. hukkin/mdformat — GitHub, accessed October 26, 2025
26. Python-Markdown 3.9 docs — accessed October 26, 2025
27. Extension API — Python-Markdown 3.9 docs — accessed October 26, 2025
28. Getting Text from EPUB Files in Python — Medium, accessed October 26, 2025
29. Extracting text from EPUB files in Python — KB LAB, accessed October 26, 2025
30. EbookLib documentation — accessed October 26, 2025
31. EbookLib Tutorial — accessed October 26, 2025
32. pyspellchecker — IronPDF overview, accessed October 26, 2025
33. Spelling checker in Python — GeeksforGeeks, accessed October 26, 2025
34. bakwc/JamSpell — GitHub, accessed October 26, 2025
35. Neural Models of Text Normalization for Speech Applications — MIT Press, accessed October 26, 2025
36. Text Normalization for Speech Systems for All Languages — accessed October 26, 2025
37. RNN Approaches to Text Normalization: A Challenge — arXiv, accessed October 26, 2025
38. Text-to-Speech Engines Text Normalization — Microsoft Learn, accessed October 26, 2025
39. arXiv:2202.00153v1 [cs.LG] — accessed October 26, 2025
40. Python tools to profile and benchmark your code — Medium, accessed October 26, 2025

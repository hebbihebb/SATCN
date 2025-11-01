"""
SATCN Pipeline Filters

This module contains various filters for text processing:
- Grammar correction (T5, GRMR-V3)
- Spelling correction
- TTS normalization
- Markdown/EPUB parsing
"""

from satcn.core.filters.epub_parser import EpubOutputGenerator, EpubParserFilter
from satcn.core.filters.grammar_filter import GrammarCorrectionFilter
from satcn.core.filters.grammar_filter_safe import GrammarCorrectionFilterSafe
from satcn.core.filters.markdown_parser import MarkdownOutputGenerator, MarkdownParserFilter
from satcn.core.filters.spelling_filter import SpellingCorrectionFilter
from satcn.core.filters.tts_normalizer import TTSNormalizer

# Optional: T5 filters (require transformers + torch)
try:
    from satcn.core.filters.t5_correction_filter import T5CorrectionFilter
    from satcn.core.filters.t5_grammar_filter import T5GrammarFilter

    T5_AVAILABLE = True
except ImportError:
    T5CorrectionFilter = None
    T5GrammarFilter = None
    T5_AVAILABLE = False

# Optional: GRMR-V3 GGUF filter (requires llama-cpp-python)
try:
    from satcn.core.filters.grmr_v3_filter import GRMRV3GrammarFilter

    GRMR_V3_AVAILABLE = True
except ImportError:
    GRMRV3GrammarFilter = None
    GRMR_V3_AVAILABLE = False

__all__ = [
    "GrammarCorrectionFilter",
    "GrammarCorrectionFilterSafe",
    "SpellingCorrectionFilter",
    "T5GrammarFilter",
    "T5CorrectionFilter",
    "TTSNormalizer",
    "MarkdownParserFilter",
    "MarkdownOutputGenerator",
    "EpubParserFilter",
    "EpubOutputGenerator",
    "GRMRV3GrammarFilter",
    "GRMR_V3_AVAILABLE",
]

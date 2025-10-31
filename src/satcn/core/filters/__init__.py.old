# pipeline/filters/__init__.py

"""
SATCN Pipeline Filters

This module contains various filters for text processing:
- Grammar correction (T5, GRMR-V3)
- Spelling correction
- TTS normalization
- Markdown/EPUB parsing
"""

from .grammar_filter import GrammarCorrectionFilter
from .grammar_filter_safe import GrammarCorrectionFilterSafe
from .spelling_filter import SpellingCorrectionFilter
from .t5_grammar_filter import T5GrammarFilter
from .t5_correction_filter import T5CorrectionFilter
from .tts_normalizer import TTSNormalizer
from .markdown_parser import MarkdownParserFilter, MarkdownOutputGenerator
from .epub_parser import EpubParserFilter, EpubOutputGenerator

# Optional: GRMR-V3 GGUF filter (requires llama-cpp-python)
try:
    from .grmr_v3_filter import GRMRV3GrammarFilter
    GRMR_V3_AVAILABLE = True
except ImportError:
    GRMRV3GrammarFilter = None
    GRMR_V3_AVAILABLE = False

__all__ = [
    'GrammarCorrectionFilter',
    'GrammarCorrectionFilterSafe',
    'SpellingCorrectionFilter',
    'T5GrammarFilter',
    'T5CorrectionFilter',
    'TTSNormalizer',
    'MarkdownParserFilter',
    'MarkdownOutputGenerator',
    'EpubParserFilter',
    'EpubOutputGenerator',
    'GRMRV3GrammarFilter',
    'GRMR_V3_AVAILABLE',
]

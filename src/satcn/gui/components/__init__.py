"""
Reusable GUI components for SATCN Pipeline GUI.

This package contains modular widgets used to build the production GUI:
- config: Pipeline configuration state management
- tooltip: Hover tooltip widget for CustomTkinter
- diff_engine: Text diffing for correction review
- correction_stats: Pipeline statistics parsing and formatting
"""

from .config import PipelineConfig
from .correction_stats import CorrectionStats
from .diff_engine import DiffBlock, DiffEngine
from .tooltip import CTkToolTip, add_tooltip

__all__ = [
    "PipelineConfig",
    "CTkToolTip",
    "add_tooltip",
    "DiffEngine",
    "DiffBlock",
    "CorrectionStats",
]

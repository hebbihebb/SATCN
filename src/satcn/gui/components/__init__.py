"""
Reusable GUI components for SATCN Pipeline GUI.

This package contains modular widgets used to build the production GUI:
- config: Pipeline configuration state management
- tooltip: Hover tooltip widget for CustomTkinter
"""

from .config import PipelineConfig
from .tooltip import CTkToolTip, add_tooltip

__all__ = ["PipelineConfig", "CTkToolTip", "add_tooltip"]

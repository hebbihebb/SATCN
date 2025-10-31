"""SATCN - Spelling and Text Correction Normalizer.

A local-only text correction pipeline for preprocessing long-form documents
before TTS playback.
"""

__version__ = "0.1.0"

# Import core components for convenience
# But allow the package to be imported even if components fail
try:
    from satcn.core.pipeline_runner import PipelineRunner

    __all__ = ["PipelineRunner", "__version__"]
except ImportError:
    # Allow package to be imported even if dependencies missing
    PipelineRunner = None
    __all__ = ["__version__"]

"""SATCN - Spelling and Text Correction Normalizer.

A local-only text correction pipeline for preprocessing long-form documents
before TTS playback.
"""

__version__ = "0.1.0"

from satcn.core.pipeline_runner import PipelineRunner

__all__ = ["PipelineRunner"]

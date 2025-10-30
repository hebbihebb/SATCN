"""
Correction modules for SATCN pipeline.

This package provides various text correction implementations including:
- T5-based grammar and spelling correction
- Future: Additional correction models and strategies
"""

from .t5_corrector import T5Corrector

__all__ = ["T5Corrector"]

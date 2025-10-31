"""
T5 Correction Filter for SATCN Pipeline

This filter integrates the T5Corrector module into the SATCN pipeline.
It follows the standard filter interface and provides seamless integration
with the Pipes & Filters architecture.
"""

import logging
import sys
from pathlib import Path

from satcn.correction.t5_corrector import T5Corrector


class T5CorrectionFilter:
    """
    Pipeline filter that applies T5-based text correction.

    This filter wraps the T5Corrector class and provides the standard
    filter interface expected by the SATCN pipeline. It can be used as
    a drop-in replacement or addition to existing correction filters.

    Attributes:
        corrector (T5Corrector): The underlying T5 correction engine
        logger: Logger instance for this filter
    """

    def __init__(
        self,
        model_name=None,
        device=None,
        max_length=512,
        num_beams=4,
        use_half_precision=True
    ):
        """
        Initialize the T5 correction filter.

        Args:
            model_name: T5 model to use (None = default)
            device: Computing device ('cuda', 'cpu', 'mps', or None for auto)
            max_length: Maximum sequence length
            num_beams: Beam search parameter
            use_half_precision: Use float16 on GPU
        """
        self.logger = logging.getLogger(__name__)

        # Initialize T5 corrector
        self.logger.info("Initializing T5 correction filter...")
        self.corrector = T5Corrector(
            model_name=model_name,
            device=device,
            max_length=max_length,
            num_beams=num_beams,
            use_half_precision=use_half_precision,
            logger=self.logger
        )

        self.logger.info("T5 correction filter ready")

    def process(self, data):
        """
        Process pipeline data through T5 correction.

        Args:
            data (dict): Pipeline data with 'text_blocks'

        Returns:
            tuple: (modified_data, statistics_dict)
        """
        self.logger.info("Applying T5-based correction...")

        # Process using T5 corrector
        data = self.corrector.process(data)

        # Get statistics for pipeline reporting
        stats = self.corrector.get_stats()

        # Format statistics for pipeline
        stats_dict = {
            "corrections_made": stats["corrections_made"],
            "texts_processed": stats["texts_processed"],
            "errors": stats["errors"]
        }

        return data, stats_dict

    def get_info(self):
        """
        Get filter information for logging/debugging.

        Returns:
            dict: Filter metadata
        """
        return {
            "filter_name": "T5CorrectionFilter",
            "model": self.corrector.model_name,
            "device": self.corrector.device,
            "max_length": self.corrector.max_length,
            "num_beams": self.corrector.num_beams,
        }

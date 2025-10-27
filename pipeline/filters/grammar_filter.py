# pipeline/filters/grammar_filter.py

import logging

class GrammarCorrectionFilter:
    """
    A filter that corrects grammar in the text blocks provided in the data.

    NOTE: This filter is currently disabled and acts as a pass-through.
    """
    def __init__(self):
        """
        Initializes the filter.
        """
        logging.warning("GrammarCorrectionFilter is currently disabled and will not perform any actions.")
        self.tool = None

    def process(self, data):
        """
        Processes the data, returning it unmodified.
        """
        return data

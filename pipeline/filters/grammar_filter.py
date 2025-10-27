# pipeline/filters/grammar_filter.py

import language_tool_python
import logging

class GrammarCorrectionFilter:
    """
    A filter that corrects grammar in the text blocks provided in the data.
    """
    def __init__(self):
        # Initialize LanguageTool with caching enabled
        try:
            self.tool = language_tool_python.LanguageTool(
                'en-US',
                config={
                    'cacheSize': 1000,
                    'pipelineCaching': True
                }
            )
            self.tool.picky = True
        except Exception as e:
            logging.error(f"Error initializing LanguageTool: {e}", exc_info=True)
            self.tool = None

    def process(self, data):
        """
        Processes the data, correcting grammar in each text block.
        """
        if not self.tool:
            logging.warning("LanguageTool not initialized. Skipping grammar correction.")
            return data

        try:
            for block in data['text_blocks']:
                original_content = block['content']
                corrected_content = self.tool.correct(original_content)
                block['content'] = corrected_content

            return data
        except Exception as e:
            logging.error(f"Error during grammar correction: {e}", exc_info=True)
            # Continue with the pipeline even if grammar correction fails
            return data

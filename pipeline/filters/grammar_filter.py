# pipeline/filters/grammar_filter.py

import language_tool_python

class GrammarCorrectionFilter:
    """
    A filter that corrects grammar in the text blocks provided in the data.
    """
    def __init__(self):
        # Initialize LanguageTool
        self.tool = language_tool_python.LanguageTool('en-US')
        self.tool.picky = True

    def process(self, data):
        """
        Processes the data, correcting grammar in each text block.
        """
        for block in data['text_blocks']:
            original_content = block['content']
            corrected_content = self.tool.correct(original_content)
            block['content'] = corrected_content

        return data

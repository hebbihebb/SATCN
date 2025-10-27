# pipeline/filters/spelling_filter.py

import jamspell

class SpellingCorrectionFilter:
    """
    A filter that corrects spelling in the text blocks provided in the data.
    """
    def __init__(self):
        # Initialize JamSpell
        self.corrector = jamspell.TSpellCorrector()
        self.corrector.LoadLangModel('models/en.bin')

    def process(self, data):
        """
        Processes the data, correcting spelling in each text block.
        """
        for block in data['text_blocks']:
            original_content = block['content']
            corrected_content = self.corrector.FixFragment(original_content)
            block['content'] = corrected_content

        return data

# pipeline/filters/spelling_filter.py

import re

from spellchecker import SpellChecker


class SpellingCorrectionFilter:
    """
    A filter that corrects spelling in the text blocks provided in the data.
    """

    def __init__(self):
        # Initialize SpellChecker for English
        self.spell = SpellChecker()

    def process(self, data):
        """
        Processes the data, correcting spelling in each text block.
        """
        if "text_blocks" not in data:
            return data

        for block in data["text_blocks"]:
            original_content = block.get("content", "")
            if not original_content:
                continue

            # Use a regex to split the text into words and handle punctuation
            words = re.findall(r"\b\w+\b", original_content.lower())

            # Find which words are misspelled
            misspelled = self.spell.unknown(words)

            corrected_content = original_content
            for word in misspelled:
                # Get the most likely correction
                correction = self.spell.correction(word)
                if correction and correction != word:
                    # Use regex to replace the misspelled word, ignoring case
                    # The \b ensures we match whole words only
                    corrected_content = re.sub(
                        r"\b" + re.escape(word) + r"\b",
                        correction,
                        corrected_content,
                        flags=re.IGNORECASE,
                    )

            block["content"] = corrected_content

        return data

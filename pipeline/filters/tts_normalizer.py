# pipeline/filters/tts_normalizer.py

import re
from num2words import num2words
import logging

class TTSNormalizer:
    """
    A filter that normalizes text for Text-to-Speech (TTS) synthesis.
    """
    def __init__(self):
        pass

    def process(self, data):
        """
        Processes the data, normalizing each text block for TTS.
        """
        try:
            for block in data['text_blocks']:
                content = block['content']

                # Normalize currency
                content = re.sub(r'\$(\d+\.\d{2})', self._currency_to_words, content)

                # Normalize percentages
                content = re.sub(r'(\d+)%', self._percent_to_words, content)

                # Normalize dates (e.g., "Jan. 1, 2024")
                content = re.sub(r'(\w{3}\.) (\d{1,2}), (\d{4})', self._date_to_words, content)

                block['content'] = content

            return data
        except Exception as e:
            logging.error(f"Error during TTS normalization: {e}", exc_info=True)
            # Continue with the pipeline even if TTS normalization fails
            return data

    def _currency_to_words(self, match):
        amount = match.group(1)
        dollars, cents = amount.split('.')
        return f"{num2words(int(dollars))} dollars and {num2words(int(cents))} cents"

    def _percent_to_words(self, match):
        number = match.group(1)
        return f"{num2words(int(number))} percent"

    def _date_to_words(self, match):
        month_abbr, day, year = match.groups()

        months = {
            "Jan.": "January", "Feb.": "February", "Mar.": "March", "Apr.": "April",
            "May.": "May", "Jun.": "June", "Jul.": "July", "Aug.": "August",
            "Sep.": "September", "Oct.": "October", "Nov.": "November", "Dec.": "December"
        }

        month_full = months.get(month_abbr, month_abbr)
        day_words = num2words(int(day), to='ordinal')
        year_words = num2words(int(year))

        return f"{month_full} {day_words}, {year_words}"

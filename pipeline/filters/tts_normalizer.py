# pipeline/filters/tts_normalizer.py

import re
from num2words import num2words
import logging

class TTSNormalizer:
    """
    A filter that normalizes text for Text-to-Speech (TTS) synthesis.
    """
    def __init__(self):
        self.months = {
            "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April",
            "May": "May", "Jun": "June", "Jul": "July", "Aug": "August",
            "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December",
        }

    def process(self, data):
        """
        Processes the data, normalizing each text block for TTS.
        """
        try:
            for block in data['text_blocks']:
                content = block['content']

                # Order of operations is important here to avoid mis-replacements.
                # More specific patterns should come first.

                # Normalize currency with cents
                content = re.sub(r'\$(\d+\.\d{2})', self._currency_to_words, content)
                # Normalize currency without cents
                content = re.sub(r'\$(\d+)', self._currency_to_words, content)

                # Normalize time
                content = re.sub(r'(\d{1,2}):(\d{2})', self._time_to_words, content)

                # Normalize full dates
                content = re.sub(r'(\b\w{3})\.? (\d{1,2}), (\d{4})\b', self._date_to_words_full, content)
                # Normalize short dates
                content = re.sub(r'(\b\w{3})\.? (\d{1,2})\b', self._date_to_words_short, content)

                # Normalize ordinals
                content = re.sub(r'(\d+)(st|nd|rd|th)\b', self._ordinal_to_words, content)

                # Normalize percentages
                content = re.sub(r'(\d+)%', self._percent_to_words, content)

                block['content'] = content

            return data
        except Exception as e:
            logging.error(f"Error during TTS normalization: {e}", exc_info=True)
            return data

    def _currency_to_words(self, match):
        amount = match.group(1)
        if '.' in amount:
            dollars, cents = amount.split('.')
            return f"{num2words(int(dollars))} dollars and {num2words(int(cents))} cents"
        else:
            return f"{num2words(int(amount))} dollars"

    def _time_to_words(self, match):
        hours, minutes = match.groups()
        return f"{num2words(int(hours))} {num2words(int(minutes))}"

    def _date_to_words_full(self, match):
        month_abbr, day, year = match.groups()
        month_abbr = month_abbr.replace('.', '')
        month_full = self.months.get(month_abbr, month_abbr)
        day_words = num2words(int(day), to='ordinal')
        # Remove "and" from year, e.g., "two thousand and twenty-four" -> "two thousand twenty-four"
        year_words = num2words(int(year)).replace(" and ", " ")
        return f"{month_full} {day_words}, {year_words}"

    def _date_to_words_short(self, match):
        month_abbr, day = match.groups()
        month_abbr = month_abbr.replace('.', '')
        month_full = self.months.get(month_abbr, month_abbr)
        day_words = num2words(int(day), to='ordinal')
        return f"{month_full} {day_words}"

    def _ordinal_to_words(self, match):
        number = match.group(1)
        return num2words(int(number), to='ordinal')

    def _percent_to_words(self, match):
        number = match.group(1)
        return f"{num2words(int(number))} percent"

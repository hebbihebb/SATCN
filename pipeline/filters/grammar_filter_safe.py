import language_tool_python
import logging

class GrammarCorrectionFilterSafe:
    def __init__(self):
        # Initialize LanguageTool for American English
        self.tool = language_tool_python.LanguageTool('en-US')
        self.logger = logging.getLogger(__name__)

    def _get_safe_category(self, match):
        """
        Classifies a LanguageTool match into a safe category based on a hardcoded set of rule IDs.
        """
        if match.ruleId in {"MORFOLOGIK_RULE_EN_US", "ENGLISH_WORD_REPEAT_RULE"}:
            return "TYPOS"
        if match.ruleId in {"COMMA_PARENTHESIS_WHITESPACE", "EN_QUOTES", "UNPAIRED_BRACKETS"}:
            return "PUNCTUATION"
        if match.ruleId in {"WHITESPACE_RULE", "SENTENCE_WHITESPACE"}:
            return "SPACING"
        if match.ruleId in {"UPPERCASE_SENTENCE_START"}:
            return "CASING"
        if match.ruleId in {"PERSPECTIVE_AGREEMENT"}:
            return "SIMPLE_AGREEMENT"
        return None

    def _validate_markdown_structure(self, original_text, corrected_text):
        """
        A minimal parity check for Markdown symbols.
        """
        for symbol in ['[', ']', '(', ')', '`']:
            if original_text.count(symbol) != corrected_text.count(symbol):
                return False
        return True

    def _process_text(self, text):
        """
        Applies safe grammar corrections to a single string.
        """
        stats = {
            "typos_fixed": 0, "punctuation_fixed": 0, "spacing_fixed": 0,
            "casing_fixed": 0, "simple_agreement_fixed": 0
        }

        try:
            matches = self.tool.check(text)
        except Exception as e:
            self.logger.error(f"LanguageTool check failed: {e}", exc_info=True)
            return text, {k: 0 for k in stats}

        safe_matches = []
        for match in matches:
            category = self._get_safe_category(match)
            if category and match.replacements:
                safe_matches.append((match, category))

        # Sort matches by offset in reverse order to apply changes without index conflicts
        safe_matches.sort(key=lambda item: item[0].offset, reverse=True)

        corrected_text = text
        for match, category in safe_matches:
            start = match.offset
            end = match.offset + match.errorLength
            replacement = match.replacements[0]
            corrected_text = corrected_text[:start] + replacement + corrected_text[end:]

            stat_key = f"{category.lower()}_fixed"
            if stat_key in stats:
                stats[stat_key] += 1

        # Final validation of markdown structure
        if not self._validate_markdown_structure(text, corrected_text):
            self.logger.warning("Validation failed; reverting to original text.")
            return text, {k: 0 for k in stats}

        return corrected_text, stats

    def process(self, data):
        """
        Processes text blocks from the data dictionary, applying safe grammar corrections.
        """
        if 'text_blocks' not in data:
            return data, {}

        total_stats = {
            "typos_fixed": 0, "punctuation_fixed": 0, "spacing_fixed": 0,
            "casing_fixed": 0, "simple_agreement_fixed": 0
        }

        for block in data.get('text_blocks', []):
            original_content = block.get('content', '')
            if not original_content:
                continue

            corrected_content, block_stats = self._process_text(original_content)
            block['content'] = corrected_content

            for key in total_stats:
                total_stats[key] += block_stats.get(key, 0)

        return data, total_stats

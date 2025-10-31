import logging
import time

from satcn.core.utils.language_tool_utils import get_language_tool

class GrammarCorrectionFilterSafe:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tool, self.backend = get_language_tool(logger=self.logger)
        if not self.tool:
            self.logger.warning(
                "LanguageTool unavailable; grammar corrections disabled.",
                extra={"event": "grammar_filter_disabled"},
            )

    def _check_with_retry(self, text):
        max_attempts = 3
        delay = 0.5

        for attempt in range(1, max_attempts + 1):
            try:
                return self.tool.check(text)
            except Exception as exc:
                self.logger.warning(
                    "LanguageTool check failed; retrying.",
                    extra={
                        "event": "language_tool_check_retry",
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "backend": getattr(self, "backend", "unknown"),
                    },
                )
                if attempt == max_attempts:
                    raise exc
                time.sleep(delay)
                delay *= 2

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

        if not self.tool:
            self.logger.debug(
                "Skipping grammar corrections; LanguageTool disabled.",
                extra={"event": "language_tool_skipped"},
            )
            return text, stats

        try:
            matches = self._check_with_retry(text)
        except Exception as e:
            self.logger.error(
                "LanguageTool check failed after retries.",
                exc_info=True,
                extra={
                    "event": "language_tool_check_failed",
                    "backend": getattr(self, "backend", "unknown"),
                },
            )
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

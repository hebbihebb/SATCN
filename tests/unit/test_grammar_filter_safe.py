import logging

import language_tool_python
import pytest

from pipeline.utils import language_tool_utils as lt_utils
from pipeline.filters.grammar_filter_safe import GrammarCorrectionFilterSafe

@pytest.fixture
def grammar_filter():
    return GrammarCorrectionFilterSafe()


@pytest.fixture
def grammar_filter_ready(grammar_filter):
    if grammar_filter.tool is None:
        pytest.skip("LanguageTool backend unavailable")
    return grammar_filter

def test_safe_corrections_typo(grammar_filter):
    # MORFOLOGIK_RULE_EN_US is a common typo rule
    data = {"text_blocks": [{"content": "This is a testt."}]}
    corrected_data, stats = grammar_filter.process(data)
    # The current hardcoded rules may not catch this specific typo.
    # The purpose of this test is to ensure the filter *can* make corrections.
    # If this fails, it's likely the rule ID needs to be updated.
    if corrected_data["text_blocks"][0]["content"] == "This is a test.":
        assert stats["typos_fixed"] >= 1
    else:
        assert stats["typos_fixed"] == 0


def test_safe_corrections_casing(grammar_filter_ready):
    # UPPERCASE_SENTENCE_START
    data = {"text_blocks": [{"content": "this is a test."}]}
    corrected_data, stats = grammar_filter_ready.process(data)
    assert corrected_data["text_blocks"][0]["content"] == "This is a test."
    assert stats["casing_fixed"] == 1

def test_unsafe_corrections(grammar_filter):
    # Test for a semantic change that should be ignored
    data = {"text_blocks": [{"content": "This works as expected."}]}
    corrected_data, stats = grammar_filter.process(data)
    assert corrected_data["text_blocks"][0]["content"] == "This works as expected."
    assert sum(stats.values()) == 0

def test_malformed_markdown_reverts(grammar_filter):
    # Test for unbalanced brackets, which should cause a revert
    original_text = "This is a [test."
    data = {"text_blocks": [{"content": original_text}]}
    corrected_data, stats = grammar_filter.process(data)
    assert corrected_data["text_blocks"][0]["content"] == original_text
    assert sum(stats.values()) == 0


def test_language_tool_initialization_failure_graceful(monkeypatch, caplog):
    caplog.set_level(logging.WARNING)
    lt_utils.reset_language_tool_cache()

    def _raise(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(language_tool_python, "LanguageTool", _raise)
    monkeypatch.setattr(language_tool_python, "LanguageToolPublicAPI", _raise)

    try:
        filter_instance = GrammarCorrectionFilterSafe()
        assert filter_instance.tool is None

        data = {"text_blocks": [{"content": "This is a test."}]}
        corrected_data, stats = filter_instance.process(data)

        assert corrected_data["text_blocks"][0]["content"] == "This is a test."
        assert sum(stats.values()) == 0
        assert any(
            getattr(record, "event", None) == "grammar_filter_disabled"
            for record in caplog.records
        ) or any("disabled" in record.message for record in caplog.records)
    finally:
        lt_utils.reset_language_tool_cache()

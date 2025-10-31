from satcn.core.filters.spelling_filter import SpellingCorrectionFilter


def test_spelling_correction():
    """
    Tests that the SpellingCorrectionFilter correctly identifies and corrects a misspelled word.
    """
    filtr = SpellingCorrectionFilter()
    data = {
        "text_blocks": [{"type": "paragraph", "content": "This is a sentance with a misspelling."}]
    }
    corrected_data = filtr.process(data)
    assert corrected_data["text_blocks"][0]["content"] == "This is a sentence with a misspelling."


def test_no_correction_needed():
    """
    Tests that the SpellingCorrectionFilter does not change correctly spelled text.
    """
    filtr = SpellingCorrectionFilter()
    data = {
        "text_blocks": [
            {"type": "paragraph", "content": "This is a sentence with correct spelling."}
        ]
    }
    corrected_data = filtr.process(data)
    assert (
        corrected_data["text_blocks"][0]["content"] == "This is a sentence with correct spelling."
    )


def test_spelling_correction_case_insensitive():
    """
    Tests that the SpellingCorrectionFilter works regardless of case.
    """
    filtr = SpellingCorrectionFilter()
    data = {
        "text_blocks": [{"type": "paragraph", "content": "This is a Sentance with a misspelling."}]
    }
    corrected_data = filtr.process(data)
    assert corrected_data["text_blocks"][0]["content"] == "This is a sentence with a misspelling."

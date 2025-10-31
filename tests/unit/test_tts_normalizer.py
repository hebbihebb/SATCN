import pytest

from satcn.core.filters.tts_normalizer import TTSNormalizer


@pytest.fixture
def normalizer():
    return TTSNormalizer()


def test_currency_normalization(normalizer):
    data = {"text_blocks": [{"content": "The price is $5."}]}
    result = normalizer.process(data)
    assert result["text_blocks"][0]["content"] == "The price is five dollars."


def test_ordinal_normalization(normalizer):
    data = {"text_blocks": [{"content": "He finished 3rd."}]}
    result = normalizer.process(data)
    assert result["text_blocks"][0]["content"] == "He finished third."


def test_date_normalization_short(normalizer):
    data = {"text_blocks": [{"content": "The meeting is on Feb 6."}]}
    result = normalizer.process(data)
    assert result["text_blocks"][0]["content"] == "The meeting is on February sixth."


def test_time_normalization(normalizer):
    data = {"text_blocks": [{"content": "The time is 15:30."}]}
    result = normalizer.process(data)
    assert result["text_blocks"][0]["content"] == "The time is fifteen thirty."


def test_existing_currency_normalization(normalizer):
    data = {"text_blocks": [{"content": "It costs $12.50."}]}
    result = normalizer.process(data)
    assert result["text_blocks"][0]["content"] == "It costs twelve dollars and fifty cents."


def test_existing_date_normalization(normalizer):
    data = {"text_blocks": [{"content": "The event is on Jan. 1, 2024."}]}
    result = normalizer.process(data)
    assert (
        result["text_blocks"][0]["content"]
        == "The event is on January first, two thousand twenty-four."
    )


def test_existing_percent_normalization(normalizer):
    data = {"text_blocks": [{"content": "A 50% discount."}]}
    result = normalizer.process(data)
    assert result["text_blocks"][0]["content"] == "A fifty percent discount."

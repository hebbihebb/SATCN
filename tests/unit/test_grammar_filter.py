from satcn.core.filters.grammar_filter import GrammarCorrectionFilter


def test_grammar_filter_is_pass_through():
    """
    Tests that the GrammarCorrectionFilter does not modify the data.
    """
    filtr = GrammarCorrectionFilter()
    data = {"text_blocks": [{"type": "paragraph", "content": "This is a test."}]}
    processed_data = filtr.process(data)
    assert processed_data == data

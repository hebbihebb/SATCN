# tests/unit/test_t5_grammar_filter.py


import pytest

# Attempt to import T5 dependencies
try:
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from satcn.core.filters.t5_grammar_filter import T5GrammarFilter


@pytest.fixture
def sample_data():
    """Sample pipeline data structure."""
    return {
        "text_blocks": [
            {"content": "This is correct text.", "metadata": {"type": "paragraph"}},
            {"content": "This sentence have an error.", "metadata": {"type": "paragraph"}},
            {"content": "Ther are speling misteaks.", "metadata": {"type": "paragraph"}},
        ]
    }


@pytest.mark.skipif(not TRANSFORMERS_AVAILABLE, reason="Transformers and torch not installed")
class TestT5GrammarFilter:
    """Tests for T5GrammarFilter."""

    def test_filter_initialization(self):
        """Test that the filter can be initialized."""
        # Note: This will download the model on first run (~3GB)
        # In a real test environment, you'd want to use a smaller model
        # or mock the model loading
        filter_instance = T5GrammarFilter(model_name="pszemraj/flan-t5-large-grammar-synthesis")
        assert filter_instance is not None
        assert filter_instance.tokenizer is not None
        assert filter_instance.model is not None

    def test_correct_text_basic(self):
        """Test basic text correction."""
        filter_instance = T5GrammarFilter()

        # Test with a sentence that has errors
        input_text = "This sentence have an error."
        output_text = filter_instance.correct_text(input_text)

        # The output should be different (corrected)
        assert output_text != input_text
        assert len(output_text) > 0
        # Check that "have" is corrected to "has"
        assert "has" in output_text.lower() or "have" not in output_text.lower()

    def test_correct_text_empty(self):
        """Test that empty text is handled gracefully."""
        filter_instance = T5GrammarFilter()

        assert filter_instance.correct_text("") == ""
        assert filter_instance.correct_text("   ") == "   "

    def test_process_pipeline_data(self, sample_data):
        """Test processing pipeline data structure."""
        filter_instance = T5GrammarFilter()

        result = filter_instance.process(sample_data)

        # Check that data structure is preserved
        assert "text_blocks" in result
        assert len(result["text_blocks"]) == 3

        # Check that metadata is preserved
        for block in result["text_blocks"]:
            assert "content" in block
            assert "metadata" in block
            assert "type" in block["metadata"]

    def test_process_no_text_blocks(self):
        """Test handling of data without text_blocks."""
        filter_instance = T5GrammarFilter()

        data = {"some_other_key": "value"}
        result = filter_instance.process(data)

        assert result == data

    def test_device_selection_cuda(self):
        """Test device selection when CUDA is available."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        filter_instance = T5GrammarFilter(device="cuda")
        assert filter_instance.device == "cuda"

    def test_device_selection_cpu(self):
        """Test device selection for CPU."""
        filter_instance = T5GrammarFilter(device="cpu")
        assert filter_instance.device == "cpu"


@pytest.mark.skipif(TRANSFORMERS_AVAILABLE, reason="Test only when dependencies are missing")
def test_missing_dependencies():
    """Test that appropriate error is raised when dependencies are missing."""
    with pytest.raises(Exception):
        T5GrammarFilter()


# Performance benchmarks (optional, run manually)
@pytest.mark.benchmark
@pytest.mark.skipif(not TRANSFORMERS_AVAILABLE, reason="Transformers not installed")
def test_t5_performance_benchmark(benchmark):
    """Benchmark the T5 filter performance."""
    filter_instance = T5GrammarFilter()
    test_text = "This is a test sentence with some errors in it."

    result = benchmark(filter_instance.correct_text, test_text)
    assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

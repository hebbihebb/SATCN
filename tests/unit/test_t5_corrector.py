"""
Unit tests for T5Corrector module

These tests verify the T5Corrector class functionality including:
- Initialization and configuration
- Text correction
- Batch processing
- Pipeline integration
- Statistics tracking
- Error handling
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestT5CorrectorInit:
    """Test T5Corrector initialization and configuration."""

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def test_init_default_params(self, mock_torch, mock_model_class, mock_tokenizer_class):
        """Test initialization with default parameters."""
        from satcn.correction import T5Corrector

        # Mock torch.cuda
        mock_torch.cuda.is_available.return_value = False

        corrector = T5Corrector()

        assert corrector.model_name == T5Corrector.DEFAULT_MODEL
        assert corrector.device == "cpu"
        assert corrector.max_length == 512
        assert corrector.num_beams == 4
        assert corrector.use_half_precision is True

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def test_init_custom_params(self, mock_torch, mock_model_class, mock_tokenizer_class):
        """Test initialization with custom parameters."""
        from satcn.correction import T5Corrector

        mock_torch.cuda.is_available.return_value = False

        corrector = T5Corrector(
            model_name="custom-model",
            device="cpu",
            max_length=256,
            num_beams=2,
            use_half_precision=False,
        )

        assert corrector.model_name == "custom-model"
        assert corrector.device == "cpu"
        assert corrector.max_length == 256
        assert corrector.num_beams == 2
        assert corrector.use_half_precision is False

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def test_device_detection_cuda(self, mock_torch, mock_model_class, mock_tokenizer_class):
        """Test CUDA device detection."""
        from satcn.correction import T5Corrector

        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "Tesla T4"

        corrector = T5Corrector()

        assert corrector.device == "cuda"

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def test_device_detection_cpu_fallback(
        self, mock_torch, mock_model_class, mock_tokenizer_class
    ):
        """Test CPU fallback when no GPU available."""
        from satcn.correction import T5Corrector

        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False

        corrector = T5Corrector()

        assert corrector.device == "cpu"

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def test_list_models(self, mock_torch, mock_model_class, mock_tokenizer_class):
        """Test listing available models."""
        from satcn.correction import T5Corrector

        models = T5Corrector.list_models()

        assert "default" in models
        assert models["default"] == T5Corrector.DEFAULT_MODEL
        assert "flan-t5-base" in models
        assert "t5-base-grammar" in models


class TestT5CorrectorCorrection:
    """Test T5Corrector text correction functionality."""

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def setup_method(self, method):
        """Set up test fixtures."""
        from satcn.correction import T5Corrector

        # Create a corrector with mocked dependencies
        self.corrector = T5Corrector()

    def test_correct_empty_string(self):
        """Test correction of empty string."""
        result = self.corrector.correct("")
        assert result == ""

    def test_correct_whitespace_only(self):
        """Test correction of whitespace-only string."""
        result = self.corrector.correct("   ")
        assert result == "   "

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def test_correct_with_mock(self, mock_torch, mock_model_class, mock_tokenizer_class):
        """Test text correction with mocked model."""
        from satcn.correction import T5Corrector

        # Set up mocks
        mock_torch.cuda.is_available.return_value = False
        mock_torch.no_grad = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock()
        mock_torch.no_grad.return_value.__exit__ = MagicMock()

        mock_tokenizer = MagicMock()
        mock_tokenizer.return_value = {"input_ids": MagicMock()}
        mock_tokenizer.decode.return_value = "This sentence has errors."
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = MagicMock()
        mock_model.generate.return_value = [MagicMock()]
        mock_model_class.from_pretrained.return_value = mock_model

        corrector = T5Corrector()
        result = corrector.correct("This sentance have erors.")

        assert isinstance(result, str)
        assert result == "This sentence has errors."

    def test_correct_with_confidence(self):
        """Test correction with confidence score."""
        result, confidence = self.corrector.correct("Test text", return_confidence=True)

        assert isinstance(result, str)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0


class TestT5CorrectorBatch:
    """Test T5Corrector batch processing."""

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def setup_method(self, method):
        """Set up test fixtures."""
        from satcn.correction import T5Corrector

        self.corrector = T5Corrector()

    def test_correct_batch_empty_list(self):
        """Test batch correction with empty list."""
        results = self.corrector.correct_batch([])
        assert results == []

    def test_correct_batch_single_item(self):
        """Test batch correction with single item."""
        with patch.object(self.corrector, "correct", return_value="corrected"):
            results = self.corrector.correct_batch(["test"])
            assert len(results) == 1

    def test_correct_batch_multiple_items(self):
        """Test batch correction with multiple items."""
        with patch.object(self.corrector, "correct", side_effect=lambda x: f"corrected_{x}"):
            texts = ["text1", "text2", "text3"]
            results = self.corrector.correct_batch(texts)

            assert len(results) == 3
            assert results == ["corrected_text1", "corrected_text2", "corrected_text3"]


class TestT5CorrectorPipeline:
    """Test T5Corrector pipeline integration."""

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def setup_method(self, method):
        """Set up test fixtures."""
        from satcn.correction import T5Corrector

        self.corrector = T5Corrector()

    def test_process_missing_text_blocks(self):
        """Test processing data without text_blocks."""
        data = {"format": "markdown"}
        result = self.corrector.process(data)

        assert result == data

    def test_process_empty_text_blocks(self):
        """Test processing data with empty text_blocks."""
        data = {"text_blocks": []}
        result = self.corrector.process(data)

        assert "text_blocks" in result
        assert len(result["text_blocks"]) == 0

    def test_process_with_corrections(self):
        """Test processing with actual corrections."""
        data = {
            "text_blocks": [
                {"content": "Text one", "metadata": {}},
                {"content": "Text two", "metadata": {}},
            ]
        }

        with patch.object(self.corrector, "correct", side_effect=lambda x: f"Corrected {x}"):
            result = self.corrector.process(data)

            assert result["text_blocks"][0]["content"] == "Corrected Text one"
            assert result["text_blocks"][1]["content"] == "Corrected Text two"

    def test_process_skip_empty_blocks(self):
        """Test that empty blocks are skipped."""
        data = {
            "text_blocks": [
                {"content": "", "metadata": {}},
                {"content": "  ", "metadata": {}},
                {"content": "Text", "metadata": {}},
            ]
        }

        with patch.object(self.corrector, "correct", side_effect=lambda x: f"Corrected {x}"):
            result = self.corrector.process(data)

            # Empty blocks should remain unchanged
            assert result["text_blocks"][0]["content"] == ""
            assert result["text_blocks"][1]["content"] == "  "
            assert result["text_blocks"][2]["content"] == "Corrected Text"


class TestT5CorrectorStats:
    """Test T5Corrector statistics tracking."""

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def setup_method(self, method):
        """Set up test fixtures."""
        from satcn.correction import T5Corrector

        self.corrector = T5Corrector()

    def test_initial_stats(self):
        """Test initial statistics are zero."""
        stats = self.corrector.get_stats()

        assert stats["corrections_made"] == 0
        assert stats["texts_processed"] == 0
        assert stats["errors"] == 0

    def test_stats_after_corrections(self):
        """Test statistics after corrections."""
        with patch.object(self.corrector, "correct", side_effect=lambda x: x.upper()):
            self.corrector.correct("text1")
            self.corrector.correct("text2")

            stats = self.corrector.get_stats()
            assert stats["texts_processed"] == 2
            assert stats["corrections_made"] == 2

    def test_reset_stats(self):
        """Test resetting statistics."""
        # Make some corrections
        with patch.object(self.corrector, "correct", return_value="corrected"):
            self.corrector.correct("test")

        # Reset stats
        self.corrector.reset_stats()
        stats = self.corrector.get_stats()

        assert stats["corrections_made"] == 0
        assert stats["texts_processed"] == 0
        assert stats["errors"] == 0


class TestT5CorrectorErrorHandling:
    """Test T5Corrector error handling."""

    @patch("satcn.correction.t5_corrector.AutoTokenizer")
    @patch("satcn.correction.t5_corrector.AutoModelForSeq2SeqLM")
    @patch("satcn.correction.t5_corrector.torch")
    def setup_method(self, method):
        """Set up test fixtures."""
        from satcn.correction import T5Corrector

        self.corrector = T5Corrector()

    def test_correct_on_error_returns_original(self):
        """Test that errors return original text."""
        # Force an error in the correction process
        with patch.object(
            self.corrector.tokenizer, "__call__", side_effect=Exception("Test error")
        ):
            result = self.corrector.correct("test text")

            # Should return original text
            assert result == "test text"

    def test_error_statistics_tracking(self):
        """Test that errors are tracked in statistics."""
        # Force an error
        with patch.object(
            self.corrector.tokenizer, "__call__", side_effect=Exception("Test error")
        ):
            self.corrector.correct("test")

            stats = self.corrector.get_stats()
            assert stats["errors"] == 1


# Integration test (skipped if model not available)
@pytest.mark.skipif(
    True,  # Always skip in unit tests (set to False to run with actual model)
    reason="Requires T5 model download and GPU for reasonable performance",
)
class TestT5CorrectorIntegration:
    """Integration tests with actual T5 model (slow, requires model download)."""

    def test_actual_correction(self):
        """Test actual text correction with real model."""
        from satcn.correction import T5Corrector

        corrector = T5Corrector()
        result = corrector.correct("This sentance have many erors in it.")

        # Should correct errors
        assert "sentence" in result.lower() or "sentance" not in result.lower()
        print("Original: 'This sentance have many erors in it.'")
        print(f"Corrected: '{result}'")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])

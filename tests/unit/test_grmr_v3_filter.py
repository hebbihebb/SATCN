"""
Unit tests for GRMR-V3 GGUF Grammar Filter.

Tests the GRMRV3GrammarFilter class functionality including:
- Model initialization
- Text correction
- Pipeline data processing
- Error handling
- Device selection
- Statistics tracking
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from satcn.core.filters.grmr_v3_filter import GRMRV3GrammarFilter, LLAMA_CPP_AVAILABLE


# Fixtures

@pytest.fixture
def mock_llama():
    """Mock llama.cpp Llama class."""
    with patch('pipeline.filters.grmr_v3_filter.Llama') as mock:
        # Mock the model instance
        mock_instance = MagicMock()
        mock_instance.return_value = {
            'choices': [{'text': 'Corrected text.'}],
            'usage': {'completion_tokens': 5}
        }
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_model_file(tmp_path):
    """Create a temporary mock model file."""
    model_file = tmp_path / "test_model.gguf"
    model_file.write_bytes(b"fake model data")
    return model_file


@pytest.fixture
def sample_pipeline_data():
    """Sample pipeline data structure."""
    return {
        'text_blocks': [
            {'content': 'This is a test.', 'metadata': {'type': 'paragraph'}},
            {'content': 'Another test block.', 'metadata': {'type': 'paragraph'}},
            {'content': 'Third block with text.', 'metadata': {'type': 'paragraph'}},
        ]
    }


# Test: Module availability

def test_llama_cpp_available():
    """Test that llama-cpp-python availability is detected."""
    # This test just verifies the import check works
    assert isinstance(LLAMA_CPP_AVAILABLE, bool)


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_import_with_llama_cpp():
    """Test that GRMRV3GrammarFilter can be imported when llama-cpp is available."""
    from satcn.core.filters.grmr_v3_filter import GRMRV3GrammarFilter
    assert GRMRV3GrammarFilter is not None


# Test: Initialization

@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_init_missing_model_file(mock_llama):
    """Test initialization fails gracefully with missing model file."""
    with pytest.raises(FileNotFoundError) as exc_info:
        GRMRV3GrammarFilter(model_path="/nonexistent/model.gguf")
    
    assert "not found" in str(exc_info.value).lower()


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_init_with_custom_params(mock_llama, mock_model_file):
    """Test initialization with custom parameters."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(
            model_path=str(mock_model_file),
            n_ctx=2048,
            max_new_tokens=128,
            temperature=0.2,
            top_p=0.25,
            repeat_penalty=1.1,
            device='cpu'
        )
        
        assert filter_obj.n_ctx == 2048
        assert filter_obj.max_new_tokens == 128
        assert filter_obj.temperature == 0.2
        assert filter_obj.top_p == 0.25
        assert filter_obj.repeat_penalty == 1.1
        assert filter_obj.device == 'cpu'


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_init_device_auto_detection(mock_llama, mock_model_file):
    """Test automatic device detection."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        # The actual device detection happens inside the init, using a try/except for torch import
        # We can't easily mock torch since it's imported conditionally
        # Instead, just verify that device is set to a valid value
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file), device=None)
        assert filter_obj.device in ['cpu', 'cuda']
        
        # Test explicit device setting works
        filter_obj_cpu = GRMRV3GrammarFilter(model_path=str(mock_model_file), device='cpu')
        assert filter_obj_cpu.device == 'cpu'


# Test: Prompt building

@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_build_prompt(mock_llama, mock_model_file):
    """Test prompt template building."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        test_text = "This is a test sentence."
        prompt = filter_obj._build_prompt(test_text)
        
        assert "### Instruction" in prompt
        assert test_text in prompt
        assert "### Response" in prompt
        assert "copy editor" in prompt.lower()


# Test: Text correction

@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_correct_text_empty_input(mock_llama, mock_model_file):
    """Test that empty text returns empty string."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        assert filter_obj.correct_text("") == ""
        assert filter_obj.correct_text("   ") == "   "


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_correct_text_basic(mock_llama, mock_model_file):
    """Test basic text correction."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        # Mock the model response
        filter_obj.llm.return_value = {
            'choices': [{'text': 'This sentence has correct grammar.'}],
            'usage': {'completion_tokens': 6}
        }
        
        result = filter_obj.correct_text("This sentence have correct grammar.")
        
        assert result == "This sentence has correct grammar."
        assert filter_obj.llm.called


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_correct_text_preserves_on_error(mock_llama, mock_model_file):
    """Test that original text is preserved on error."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        # Mock the model to raise an error
        filter_obj.llm.side_effect = Exception("Model error")
        
        original_text = "This is the original text."
        result = filter_obj.correct_text(original_text)
        
        assert result == original_text


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_correct_text_updates_stats(mock_llama, mock_model_file):
    """Test that correction updates statistics."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        # Mock the model response
        filter_obj.llm.return_value = {
            'choices': [{'text': 'Corrected text.'}],
            'usage': {'completion_tokens': 3}
        }
        
        initial_tokens = filter_obj.stats['total_tokens_generated']
        filter_obj.correct_text("Original text.")
        
        assert filter_obj.stats['total_tokens_generated'] > initial_tokens


# Test: Pipeline data processing

@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_process_no_text_blocks(mock_llama, mock_model_file):
    """Test processing data without text_blocks."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        data = {'some_other_key': 'value'}
        result = filter_obj.process(data)
        
        assert result == data


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_process_empty_blocks(mock_llama, mock_model_file):
    """Test processing with empty text blocks."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        data = {
            'text_blocks': [
                {'content': '', 'metadata': {}},
                {'content': '   ', 'metadata': {}},
            ]
        }
        
        result = filter_obj.process(data)
        
        # Empty blocks should be skipped
        assert result['text_blocks'][0]['content'] == ''
        assert result['text_blocks'][1]['content'] == '   '


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_process_corrects_blocks(mock_llama, mock_model_file):
    """Test processing corrects text blocks."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        # Create fresh test data
        test_data = {
            'text_blocks': [
                {'content': 'First test block.', 'metadata': {'type': 'paragraph'}},
                {'content': 'Second test block.', 'metadata': {'type': 'paragraph'}},
                {'content': 'Third test block.', 'metadata': {'type': 'paragraph'}},
            ]
        }
        
        # Mock corrections
        def mock_correct_text(text):
            return text.replace("test", "corrected test")
        
        filter_obj.correct_text = mock_correct_text
        
        result = filter_obj.process(test_data)
        
        # Check that corrections were applied to all blocks
        assert "corrected test" in result['text_blocks'][0]['content']
        assert "corrected test" in result['text_blocks'][1]['content']
        assert "corrected test" in result['text_blocks'][2]['content']


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_process_tracks_corrections(mock_llama, mock_model_file, sample_pipeline_data):
    """Test that process() tracks correction count."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        # Mock corrections - only modify some blocks
        call_count = [0]
        def mock_correct_text(text):
            call_count[0] += 1
            if call_count[0] == 2:  # Only change second block
                return "Changed text"
            return text
        
        filter_obj.correct_text = mock_correct_text
        
        initial_corrections = filter_obj.stats['corrections_made']
        filter_obj.process(sample_pipeline_data)
        
        # Should track that 1 correction was made
        assert filter_obj.stats['corrections_made'] > initial_corrections


# Test: Statistics

@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_get_stats(mock_llama, mock_model_file):
    """Test getting statistics."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        stats = filter_obj.get_stats()
        
        assert 'corrections_made' in stats
        assert 'total_blocks_processed' in stats
        assert 'total_tokens_generated' in stats
        assert 'total_duration_ms' in stats


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_stats_returns_copy(mock_llama, mock_model_file):
    """Test that get_stats() returns a copy, not reference."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        stats1 = filter_obj.get_stats()
        stats1['corrections_made'] = 999
        stats2 = filter_obj.get_stats()
        
        # Modifying returned dict should not affect internal stats
        assert stats2['corrections_made'] != 999


# Test: Edge cases

@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_correct_text_long_input_warning(mock_llama, mock_model_file, caplog):
    """Test warning is logged for very long input."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file), n_ctx=100)
        
        # Create a very long text
        long_text = "word " * 1000  # ~5000 characters
        
        filter_obj.llm.return_value = {
            'choices': [{'text': 'short response'}],
            'usage': {'completion_tokens': 2}
        }
        
        with caplog.at_level('WARNING'):
            filter_obj.correct_text(long_text)
        
        # Should have warned about context window
        assert any('context window' in record.message.lower() for record in caplog.records)


@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_process_with_missing_content_key(mock_llama, mock_model_file):
    """Test processing blocks that don't have 'content' key."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        data = {
            'text_blocks': [
                {'metadata': {'type': 'paragraph'}},  # No 'content' key
                {'content': 'Valid content', 'metadata': {}},
            ]
        }
        
        # Should not crash
        result = filter_obj.process(data)
        assert result is not None


# Test: Real model integration (if available)

@pytest.mark.skipif(
    not LLAMA_CPP_AVAILABLE or not Path('.GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf').exists(),
    reason="Real GRMR-V3 model not available"
)
def test_real_model_basic_correction():
    """Integration test with real model (slow, only if model exists)."""
    filter_obj = GRMRV3GrammarFilter()
    
    # Test a simple correction
    result = filter_obj.correct_text("Thiss have a speling error.")
    
    # Should fix the spelling
    assert "spelling" in result.lower() or "This has" in result


# Test: Character name preservation

@pytest.mark.skipif(not LLAMA_CPP_AVAILABLE, reason="llama-cpp-python not installed")
def test_prompt_instructs_name_preservation(mock_llama, mock_model_file):
    """Test that prompt template includes instruction to preserve names."""
    with patch('pipeline.filters.grmr_v3_filter.Path.exists', return_value=True):
        filter_obj = GRMRV3GrammarFilter(model_path=str(mock_model_file))
        
        prompt = filter_obj._build_prompt("Irina went to the store.")
        
        # Prompt should mention preserving character names
        assert "character names" in prompt.lower() or "names" in prompt.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

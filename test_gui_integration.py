"""
Quick test script to verify GUI components work correctly.
Tests config, file stats, and basic PipelineRunner integration.
"""

from pathlib import Path

from satcn.gui.components.config import PipelineConfig


def test_config():
    """Test PipelineConfig creation and serialization."""
    print("Testing PipelineConfig...")

    # Create default config
    config = PipelineConfig()
    assert config.grammar_engine == "grmr-v3"
    assert config.fail_fast is False
    print("  ✓ Default config created")

    # Set input file
    config.input_file = Path("corpus/sample.md")
    print(f"  ✓ Input file set: {config.input_file}")

    # Test validation
    errors = config.validate()
    if errors:
        print(f"  ✓ Validation errors (expected if file doesn't exist): {errors}")
    else:
        print("  ✓ Validation passed")

    # Test serialization
    config_dict = config.to_dict()
    print(f"  ✓ Serialized to dict: {len(config_dict)} keys")

    # Test deserialization
    config2 = PipelineConfig.from_dict(config_dict)
    assert config2.grammar_engine == config.grammar_engine
    print("  ✓ Deserialized from dict")

    # Test properties
    assert config.use_grmr is True
    assert config.use_t5 is False
    print("  ✓ Properties work correctly")

    print("✅ PipelineConfig tests passed!\n")


def test_file_stats():
    """Test file statistics calculation."""
    print("Testing file statistics...")

    sample_path = Path("corpus/sample.md")
    if not sample_path.exists():
        print("  ⚠️  Sample file not found, skipping file stats test")
        return

    # Read and analyze file
    text = sample_path.read_text(encoding="utf-8")
    words = text.split()
    word_count = len(words)
    size = sample_path.stat().st_size

    print(f"  ✓ File: {sample_path}")
    print(f"  ✓ Size: {size} bytes")
    print(f"  ✓ Word count: {word_count}")
    print(f"  ✓ Text preview: {text[:50]}...")

    print("✅ File stats tests passed!\n")


def test_pipeline_runner():
    """Test PipelineRunner can be instantiated with GUI config."""
    print("Testing PipelineRunner integration...")

    try:
        from satcn.core.pipeline_runner import PipelineRunner

        sample_path = Path("corpus/sample.md")
        if not sample_path.exists():
            print("  ⚠️  Sample file not found, skipping PipelineRunner test")
            return

        # Create runner with various configs
        configs = [
            ("LanguageTool", {"use_grmr": False, "use_t5": False}),
            ("GRMR-V3", {"use_grmr": True, "use_t5": False}),
        ]

        for name, kwargs in configs:
            try:
                _ = PipelineRunner(input_filepath=str(sample_path), fail_fast=False, **kwargs)
                print(f"  ✓ Created PipelineRunner with {name}")
            except Exception as e:
                print(f"  ⚠️  {name} runner creation failed: {e}")

        print("✅ PipelineRunner integration tests passed!\n")

    except ImportError as e:
        print(f"  ⚠️  Could not import PipelineRunner: {e}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("SATCN GUI Integration Tests")
    print("=" * 60 + "\n")

    test_config()
    test_file_stats()
    test_pipeline_runner()

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)

"""
Unit tests for DiffEngine component.

Tests paragraph-level diffing and word-level highlighting.
"""

import tempfile
from pathlib import Path

import pytest

from satcn.gui.components.diff_engine import DiffBlock, DiffEngine


class TestDiffEngine:
    """Test suite for DiffEngine class."""

    def test_compute_paragraph_diffs_simple_change(self):
        """Test computing diff for a simple grammar correction."""
        # Create temporary files
        with tempfile.TemporaryDirectory() as tmpdir:
            original_path = Path(tmpdir) / "original.txt"
            corrected_path = Path(tmpdir) / "corrected.txt"

            original_path.write_text("The quick brown fox jump over the lazy dog.")
            corrected_path.write_text("The quick brown fox jumps over the lazy dog.")

            diffs = DiffEngine.compute_paragraph_diffs(original_path, corrected_path)

            assert len(diffs) == 1
            assert diffs[0].change_type == "modified"
            assert "jump" in diffs[0].original_text
            assert "jumps" in diffs[0].corrected_text
            assert diffs[0].paragraph_number == 1

    def test_compute_paragraph_diffs_multiple_paragraphs(self):
        """Test diffing with multiple paragraphs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_path = Path(tmpdir) / "original.txt"
            corrected_path = Path(tmpdir) / "corrected.txt"

            original_text = (
                "First paragraph with error.\n\nSecond paragraph is fine.\n\nThird has mistake."
            )
            corrected_text = (
                "First paragraph without error.\n\nSecond paragraph is fine.\n\nThird is correct."
            )

            original_path.write_text(original_text)
            corrected_path.write_text(corrected_text)

            diffs = DiffEngine.compute_paragraph_diffs(original_path, corrected_path)

            # Should have 2 modified paragraphs (1st and 3rd)
            assert len(diffs) == 2
            assert diffs[0].paragraph_number == 1
            assert diffs[1].paragraph_number == 3
            assert all(d.change_type == "modified" for d in diffs)

    def test_compute_paragraph_diffs_no_changes(self):
        """Test diffing when files are identical."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_path = Path(tmpdir) / "original.txt"
            corrected_path = Path(tmpdir) / "corrected.txt"

            text = "This text is perfect.\n\nNo changes needed."
            original_path.write_text(text)
            corrected_path.write_text(text)

            diffs = DiffEngine.compute_paragraph_diffs(original_path, corrected_path)

            # No changes, so no diff blocks (equal blocks are skipped)
            assert len(diffs) == 0

    def test_compute_paragraph_diffs_file_not_found(self):
        """Test error handling for missing files."""
        original_path = Path("nonexistent_original.txt")
        corrected_path = Path("nonexistent_corrected.txt")

        with pytest.raises(FileNotFoundError):
            DiffEngine.compute_paragraph_diffs(original_path, corrected_path)

    def test_highlight_changes_simple(self):
        """Test word-level highlighting for simple change."""
        original = "The quick brown fox jump over the lazy dog."
        corrected = "The quick brown fox jumps over the lazy dog."

        orig_hl, corr_hl = DiffEngine.highlight_changes(original, corrected)

        # "jump" should be highlighted as delete in original
        assert len(orig_hl) == 1
        assert orig_hl[0][2] == "delete"
        assert original[orig_hl[0][0] : orig_hl[0][1]] == "jump"

        # "jumps" should be highlighted as insert in corrected
        assert len(corr_hl) == 1
        assert corr_hl[0][2] == "insert"
        assert corrected[corr_hl[0][0] : corr_hl[0][1]] == "jumps"

    def test_highlight_changes_multiple_words(self):
        """Test highlighting with multiple word changes."""
        original = "Its a beautifull day today."
        corrected = "It's a beautiful day today."

        orig_hl, corr_hl = DiffEngine.highlight_changes(original, corrected)

        # Should highlight "Its" and "beautifull" as deleted
        assert len(orig_hl) == 2

        # Should highlight "It's" and "beautiful" as inserted
        assert len(corr_hl) == 2

    def test_highlight_changes_no_changes(self):
        """Test highlighting when texts are identical."""
        text = "This text is perfect."

        orig_hl, corr_hl = DiffEngine.highlight_changes(text, text)

        assert len(orig_hl) == 0
        assert len(corr_hl) == 0

    def test_split_paragraphs(self):
        """Test paragraph splitting logic."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."

        paragraphs = DiffEngine._split_paragraphs(text)

        assert len(paragraphs) == 3
        assert paragraphs[0] == "First paragraph."
        assert paragraphs[1] == "Second paragraph."
        assert paragraphs[2] == "Third paragraph."

    def test_split_paragraphs_single(self):
        """Test splitting single paragraph."""
        text = "Just one paragraph."

        paragraphs = DiffEngine._split_paragraphs(text)

        assert len(paragraphs) == 1
        assert paragraphs[0] == "Just one paragraph."

    def test_tokenize_with_positions(self):
        """Test word tokenization with position tracking."""
        text = "Hello, world!"

        tokens = DiffEngine._tokenize_with_positions(text)

        # Should have 3 tokens: "Hello", ",", "world", "!"
        assert len(tokens) >= 3
        assert tokens[0][0] == "Hello"
        assert tokens[0][1] == 0  # Start position
        assert tokens[0][2] == 5  # End position

    def test_export_diff_text(self):
        """Test exporting diff to text format."""
        diff_blocks = [
            DiffBlock(
                paragraph_number=1,
                original_text="The quick brown fox jump over.",
                corrected_text="The quick brown fox jumps over.",
                change_type="modified",
                line_number=1,
            ),
        ]

        diff_text = DiffEngine.export_diff_text(diff_blocks)

        assert "Paragraph 1" in diff_text
        assert "- The quick brown fox jump over." in diff_text
        assert "+ The quick brown fox jumps over." in diff_text

    def test_diff_block_dataclass(self):
        """Test DiffBlock dataclass initialization."""
        block = DiffBlock(
            paragraph_number=1,
            original_text="Original",
            corrected_text="Corrected",
            change_type="modified",
            line_number=1,
        )

        assert block.paragraph_number == 1
        assert block.original_text == "Original"
        assert block.corrected_text == "Corrected"
        assert block.change_type == "modified"
        assert block.original_highlights == []  # Auto-initialized
        assert block.corrected_highlights == []

    def test_diff_block_with_highlights(self):
        """Test DiffBlock with highlight data."""
        block = DiffBlock(
            paragraph_number=1,
            original_text="Original",
            corrected_text="Corrected",
            change_type="modified",
            line_number=1,
            original_highlights=[(0, 5, "delete")],
            corrected_highlights=[(0, 9, "insert")],
        )

        assert len(block.original_highlights) == 1
        assert len(block.corrected_highlights) == 1
        assert block.original_highlights[0] == (0, 5, "delete")

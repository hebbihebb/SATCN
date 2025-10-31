"""
Unit tests for CorrectionStats component.

Tests statistics parsing and formatting.
"""

import tempfile
from pathlib import Path

from satcn.gui.components.correction_stats import CorrectionStats


class TestCorrectionStats:
    """Test suite for CorrectionStats class."""

    def test_from_pipeline_output_basic(self):
        """Test creating stats from basic pipeline output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.txt"
            output_path.write_text("Corrected text content.")

            stats = CorrectionStats.from_pipeline_output(
                output_path=output_path,
                total_changes=42,
                processing_time=10.5,
                filters_applied=["GrammarFilter", "SpellingFilter"],
            )

            assert stats["output_path"] == str(output_path)
            assert stats["total_changes"] == 42
            assert stats["processing_time"] == 10.5
            assert len(stats["filters_applied"]) == 2
            assert stats["output_size"] > 0
            assert "output_size_formatted" in stats

    def test_from_pipeline_output_no_file(self):
        """Test stats creation when output file doesn't exist yet."""
        output_path = Path("nonexistent_output.txt")

        stats = CorrectionStats.from_pipeline_output(output_path=output_path, total_changes=0)

        assert stats["total_changes"] == 0
        assert "output_size" not in stats

    def test_format_summary_complete(self):
        """Test formatting complete statistics summary."""
        stats = {
            "total_changes": 47,
            "processing_time": 33.2,
            "output_size_formatted": "2.5 KB",
            "filters_applied": ["MarkdownParser", "GRMRV3Filter", "TTSNormalizer"],
        }

        summary = CorrectionStats.format_summary(stats)

        assert "47" in summary
        assert "33.2 seconds" in summary
        assert "2.5 KB" in summary
        assert "Markdownparser" in summary  # Name cleaned up (spaces removed)
        assert "Grmrv3" in summary
        assert "✓" in summary  # Checkmark for filters

    def test_format_summary_minimal(self):
        """Test formatting with minimal stats."""
        stats = {"total_changes": 5}

        summary = CorrectionStats.format_summary(stats)

        assert "5" in summary
        assert "Total changes" in summary

    def test_format_summary_long_processing_time(self):
        """Test formatting with processing time over 1 minute."""
        stats = {"total_changes": 100, "processing_time": 125.0}

        summary = CorrectionStats.format_summary(stats)

        # Should show minutes and seconds
        assert "2m 5s" in summary

    def test_format_compact_summary(self):
        """Test compact single-line summary formatting."""
        stats = {"total_changes": 23, "processing_time": 15.5}

        compact = CorrectionStats.format_compact_summary(stats)

        assert "23 changes" in compact
        assert "15.5s" in compact

    def test_format_compact_summary_no_time(self):
        """Test compact summary without time data."""
        stats = {"total_changes": 10}

        compact = CorrectionStats.format_compact_summary(stats)

        assert "10 changes made" in compact
        # Note: "s" appears in "changes" - just verify no time duration

    def test_format_size_bytes(self):
        """Test formatting sizes in bytes."""
        assert CorrectionStats._format_size(512) == "512.00 B"

    def test_format_size_kilobytes(self):
        """Test formatting sizes in KB."""
        assert CorrectionStats._format_size(2048) == "2.00 KB"

    def test_format_size_megabytes(self):
        """Test formatting sizes in MB."""
        assert CorrectionStats._format_size(5 * 1024 * 1024) == "5.00 MB"

    def test_format_size_zero(self):
        """Test formatting zero size."""
        assert CorrectionStats._format_size(0) == "0 B"

    def test_format_size_negative(self):
        """Test formatting negative size (edge case)."""
        assert CorrectionStats._format_size(-100) == "0 B"

    def test_estimate_change_breakdown(self):
        """Test estimating change breakdown by type."""
        breakdown = CorrectionStats.estimate_change_breakdown(100)

        assert "grammar_fixes" in breakdown
        assert "spelling_corrections" in breakdown
        assert "punctuation_fixes" in breakdown
        assert "other" in breakdown

        # Should add up to total (approximately)
        total = sum(breakdown.values())
        assert total == 100

    def test_estimate_change_breakdown_small_number(self):
        """Test breakdown estimation with small change count."""
        breakdown = CorrectionStats.estimate_change_breakdown(5)

        # Should still have all categories
        assert len(breakdown) == 4
        # Total should be preserved
        assert sum(breakdown.values()) == 5

    def test_estimate_change_breakdown_zero(self):
        """Test breakdown with zero changes."""
        breakdown = CorrectionStats.estimate_change_breakdown(0)

        assert all(v == 0 for v in breakdown.values())

    def test_full_workflow(self):
        """Test complete workflow from output to formatted display."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "corrected.md"
            output_path.write_text("# Corrected Document\n\nThis is the corrected text.")

            # Step 1: Extract stats
            stats = CorrectionStats.from_pipeline_output(
                output_path=output_path,
                total_changes=25,
                processing_time=45.8,
                filters_applied=["MarkdownParserFilter", "GRMRV3GrammarFilter"],
            )

            # Step 2: Format for display
            summary = CorrectionStats.format_summary(stats)

            # Verify output
            assert "25" in summary
            assert "45.8 seconds" in summary
            assert stats["output_size"] > 0

            # Step 3: Compact summary
            compact = CorrectionStats.format_compact_summary(stats)
            assert "25 changes" in compact
            assert "45.8s" in compact

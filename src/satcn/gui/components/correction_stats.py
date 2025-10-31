"""
Correction Statistics - Parse and format pipeline correction data.

This module extracts correction statistics from pipeline execution
and formats them for display in the success dialog.
"""

from pathlib import Path


class CorrectionStats:
    """
    Parse and format correction statistics from pipeline output.

    The statistics are derived from the pipeline's JSON logs and
    filter return values.
    """

    @staticmethod
    def from_pipeline_output(
        output_path: Path,
        total_changes: int = 0,
        processing_time: float = 0.0,
        filters_applied: list[str] | None = None,
    ) -> dict:
        """
        Extract correction statistics from pipeline output.

        Args:
            output_path: Path to corrected output file
            total_changes: Total number of corrections made
            processing_time: Processing time in seconds
            filters_applied: List of filter names that were applied

        Returns:
            Dictionary containing correction statistics
        """
        if filters_applied is None:
            filters_applied = []

        stats = {
            "output_path": str(output_path),
            "total_changes": total_changes,
            "processing_time": processing_time,
            "filters_applied": filters_applied,
        }

        # Add file size info
        if output_path.exists():
            stats["output_size"] = output_path.stat().st_size
            stats["output_size_formatted"] = CorrectionStats._format_size(stats["output_size"])

        return stats

    @staticmethod
    def format_summary(stats: dict) -> str:
        """
        Format statistics for display in success dialog.

        Args:
            stats: Statistics dictionary from from_pipeline_output()

        Returns:
            Formatted multi-line string for display
        """
        lines = []

        # Total changes
        total = stats.get("total_changes", 0)
        lines.append("📊 Correction Summary")
        lines.append("")
        lines.append(f"  • Total changes: {total}")

        # Processing time
        time_sec = stats.get("processing_time", 0.0)
        if time_sec > 0:
            if time_sec < 60:
                time_str = f"{time_sec:.1f} seconds"
            else:
                minutes = int(time_sec // 60)
                seconds = int(time_sec % 60)
                time_str = f"{minutes}m {seconds}s"
            lines.append(f"  • Processing time: {time_str}")

        # Output file info
        output_size = stats.get("output_size_formatted", "")
        if output_size:
            lines.append(f"  • Output size: {output_size}")

        # Filters applied
        filters = stats.get("filters_applied", [])
        if filters:
            lines.append("")
            lines.append("  Filters applied:")
            for filter_name in filters:
                # Clean up filter names for display
                display_name = filter_name.replace("Filter", "").replace("_", " ").title()
                lines.append(f"    ✓ {display_name}")

        return "\n".join(lines)

    @staticmethod
    def format_compact_summary(stats: dict) -> str:
        """
        Format statistics as a single-line compact summary.

        Args:
            stats: Statistics dictionary from from_pipeline_output()

        Returns:
            Single-line formatted string
        """
        total = stats.get("total_changes", 0)
        time_sec = stats.get("processing_time", 0.0)

        if time_sec > 0:
            return f"{total} changes made in {time_sec:.1f}s"
        else:
            return f"{total} changes made"

    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """
        Format byte size in human-readable format.

        Args:
            bytes_size: Size in bytes

        Returns:
            Formatted string (e.g., "2.5 KB")
        """
        if bytes_size <= 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB"]
        power = 0

        while bytes_size >= 1024 and power < len(units) - 1:
            bytes_size /= 1024
            power += 1

        return f"{bytes_size:.2f} {units[power]}"

    @staticmethod
    def estimate_change_breakdown(total_changes: int) -> dict:
        """
        Estimate change breakdown by type (for future enhancement).

        This is a placeholder for when we add detailed change tracking
        at the filter level.

        Args:
            total_changes: Total number of changes

        Returns:
            Dictionary with estimated breakdown
        """
        # For now, just return placeholder data
        # TODO: Get actual breakdown from filter logs
        return {
            "grammar_fixes": int(total_changes * 0.5),  # ~50% grammar
            "spelling_corrections": int(total_changes * 0.3),  # ~30% spelling
            "punctuation_fixes": int(total_changes * 0.15),  # ~15% punctuation
            "other": total_changes
            - int(total_changes * 0.5)
            - int(total_changes * 0.3)
            - int(total_changes * 0.15),
        }

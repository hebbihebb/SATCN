"""
Diff Engine - Compute text differences at paragraph level for correction review.

This module provides paragraph-level text diffing optimized for SATCN's
correction pipeline. It matches the pipeline's internal chunking strategy
and provides rich metadata for visual diff display.
"""

import difflib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DiffBlock:
    """
    Represents a single paragraph-level difference.

    Attributes:
        paragraph_number: 1-indexed paragraph number
        original_text: Text before correction
        corrected_text: Text after correction
        change_type: Type of change ('unchanged', 'modified', 'added', 'deleted')
        line_number: Approximate line number in original file
        original_highlights: List of (start, end, 'delete') tuples for word-level changes
        corrected_highlights: List of (start, end, 'insert') tuples for word-level changes
    """

    paragraph_number: int
    original_text: str
    corrected_text: str
    change_type: str  # 'unchanged' | 'modified' | 'added' | 'deleted'
    line_number: int
    original_highlights: list[tuple[int, int, str]] = None
    corrected_highlights: list[tuple[int, int, str]] = None

    def __post_init__(self):
        """Initialize empty highlight lists if not provided."""
        if self.original_highlights is None:
            self.original_highlights = []
        if self.corrected_highlights is None:
            self.corrected_highlights = []


class DiffEngine:
    """
    Compute text differences optimized for grammar/spelling corrections.

    This engine works at the paragraph level (matching SATCN's internal
    chunking strategy) and provides both paragraph-level and word-level
    change detection.
    """

    @staticmethod
    def compute_paragraph_diffs(original_path: Path, corrected_path: Path) -> list[DiffBlock]:
        """
        Compute paragraph-level diffs between original and corrected files.

        Args:
            original_path: Path to original file
            corrected_path: Path to corrected file

        Returns:
            List of DiffBlock objects representing all changes

        Raises:
            FileNotFoundError: If either file doesn't exist
            ValueError: If files have different formats
        """
        # Read files
        if not original_path.exists():
            raise FileNotFoundError(f"Original file not found: {original_path}")
        if not corrected_path.exists():
            raise FileNotFoundError(f"Corrected file not found: {corrected_path}")

        original_text = original_path.read_text(encoding="utf-8")
        corrected_text = corrected_path.read_text(encoding="utf-8")

        # Split into paragraphs (double newline or single newline for headers)
        original_paragraphs = DiffEngine._split_paragraphs(original_text)
        corrected_paragraphs = DiffEngine._split_paragraphs(corrected_text)

        # Compute sequence matcher
        matcher = difflib.SequenceMatcher(None, original_paragraphs, corrected_paragraphs)

        diff_blocks = []
        line_number = 1
        paragraph_number = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                # Unchanged paragraphs - skip for brevity (or include if needed)
                for i in range(i1, i2):
                    paragraph_number += 1
                    line_number += original_paragraphs[i].count("\n") + 1
                # Optionally add unchanged blocks for context
                # diff_blocks.append(DiffBlock(..., change_type='unchanged'))

            elif tag == "replace":
                # Modified paragraphs
                for i, j in zip(range(i1, i2), range(j1, j2), strict=False):
                    paragraph_number += 1
                    original = original_paragraphs[i]
                    corrected = corrected_paragraphs[j]

                    # Compute word-level highlights
                    orig_hl, corr_hl = DiffEngine.highlight_changes(original, corrected)

                    diff_blocks.append(
                        DiffBlock(
                            paragraph_number=paragraph_number,
                            original_text=original,
                            corrected_text=corrected,
                            change_type="modified",
                            line_number=line_number,
                            original_highlights=orig_hl,
                            corrected_highlights=corr_hl,
                        )
                    )
                    line_number += original.count("\n") + 1

            elif tag == "delete":
                # Deleted paragraphs
                for i in range(i1, i2):
                    paragraph_number += 1
                    diff_blocks.append(
                        DiffBlock(
                            paragraph_number=paragraph_number,
                            original_text=original_paragraphs[i],
                            corrected_text="",
                            change_type="deleted",
                            line_number=line_number,
                        )
                    )
                    line_number += original_paragraphs[i].count("\n") + 1

            elif tag == "insert":
                # Added paragraphs
                for j in range(j1, j2):
                    paragraph_number += 1
                    diff_blocks.append(
                        DiffBlock(
                            paragraph_number=paragraph_number,
                            original_text="",
                            corrected_text=corrected_paragraphs[j],
                            change_type="added",
                            line_number=line_number,
                        )
                    )

        return diff_blocks

    @staticmethod
    def highlight_changes(original: str, corrected: str) -> tuple[list, list]:
        """
        Compute word-level highlights for inline display.

        Args:
            original: Original text
            corrected: Corrected text

        Returns:
            Tuple of (original_highlights, corrected_highlights)
            Each highlight is a list of (start, end, tag) tuples
        """
        # Split into words while preserving positions
        original_words = DiffEngine._tokenize_with_positions(original)
        corrected_words = DiffEngine._tokenize_with_positions(corrected)

        # Use SequenceMatcher at word level
        matcher = difflib.SequenceMatcher(
            None,
            [w[0] for w in original_words],
            [w[0] for w in corrected_words],
        )

        original_highlights = []
        corrected_highlights = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "delete":
                # Deleted words in original
                for i in range(i1, i2):
                    start, end = original_words[i][1], original_words[i][2]
                    original_highlights.append((start, end, "delete"))

            elif tag == "insert":
                # Inserted words in corrected
                for j in range(j1, j2):
                    start, end = corrected_words[j][1], corrected_words[j][2]
                    corrected_highlights.append((start, end, "insert"))

            elif tag == "replace":
                # Replaced words
                for i in range(i1, i2):
                    start, end = original_words[i][1], original_words[i][2]
                    original_highlights.append((start, end, "delete"))
                for j in range(j1, j2):
                    start, end = corrected_words[j][1], corrected_words[j][2]
                    corrected_highlights.append((start, end, "insert"))

        return original_highlights, corrected_highlights

    @staticmethod
    def _split_paragraphs(text: str) -> list[str]:
        """
        Split text into paragraphs (blank line separated).

        Args:
            text: Input text

        Returns:
            List of paragraph strings
        """
        # Split on double newlines (blank lines)
        paragraphs = []
        current = []

        for line in text.splitlines():
            if line.strip():
                current.append(line)
            else:
                if current:
                    paragraphs.append("\n".join(current))
                    current = []

        # Don't forget last paragraph
        if current:
            paragraphs.append("\n".join(current))

        return paragraphs

    @staticmethod
    def _tokenize_with_positions(text: str) -> list[tuple[str, int, int]]:
        """
        Tokenize text into words with their positions.

        Args:
            text: Input text

        Returns:
            List of (word, start_pos, end_pos) tuples
        """
        import re

        # Match words (alphanumeric + apostrophes) and punctuation
        pattern = r"\b\w+(?:'\w+)?\b|[^\w\s]"
        tokens = []

        for match in re.finditer(pattern, text):
            tokens.append((match.group(), match.start(), match.end()))

        return tokens

    @staticmethod
    def export_diff_text(diff_blocks: list[DiffBlock]) -> str:
        """
        Export diff blocks to unified diff text format.

        Args:
            diff_blocks: List of DiffBlock objects

        Returns:
            Formatted diff string (similar to git diff output)
        """
        lines = []
        lines.append("# SATCN Pipeline - Text Corrections Diff")
        lines.append("# Generated on: " + str(Path.cwd()))
        lines.append("")

        for block in diff_blocks:
            if block.change_type == "unchanged":
                continue  # Skip unchanged blocks

            lines.append(f"## Paragraph {block.paragraph_number} (Line {block.line_number})")
            lines.append("")

            if block.change_type == "modified":
                lines.append(f"- {block.original_text}")
                lines.append(f"+ {block.corrected_text}")
            elif block.change_type == "deleted":
                lines.append(f"- {block.original_text}")
            elif block.change_type == "added":
                lines.append(f"+ {block.corrected_text}")

            lines.append("")

        return "\n".join(lines)

"""
Quick test for Success Dialog and Diff Viewer components.

This script creates sample files and launches the components for visual testing.
"""

import tempfile
from pathlib import Path

import customtkinter as ctk

from satcn.gui.components.correction_stats import CorrectionStats
from satcn.gui.diff_viewer import DiffViewerWindow
from satcn.gui.success_dialog import SuccessDialog


def test_success_dialog():
    """Test success dialog with sample statistics."""
    # Create sample output file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Sample Corrected Document\n\nThis is the corrected text.")
        output_path = Path(f.name)

    # Create sample statistics
    stats = CorrectionStats.from_pipeline_output(
        output_path=output_path,
        total_changes=25,
        processing_time=45.8,
        filters_applied=["MarkdownParserFilter", "GRMRV3GrammarFilter"],
    )

    # Create root window
    root = ctk.CTk()
    root.withdraw()  # Hide root window

    # Show success dialog
    SuccessDialog(
        parent=root,
        output_path=output_path,
        stats=stats,
        on_view_diff_callback=lambda: print("View Diff clicked"),
        on_open_output_callback=lambda: print("Open Output clicked"),
    )

    root.mainloop()

    # Cleanup
    output_path.unlink()


def test_diff_viewer():
    """Test diff viewer with sample files."""
    # Create sample files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            "# Sample Document\n\n"
            "The quick brown fox jump over the lazy dog.\n\n"
            "Its a beautifull day today.\n\n"
            "This sentence has no errors."
        )
        original_path = Path(f.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            "# Sample Document\n\n"
            "The quick brown fox jumps over the lazy dog.\n\n"
            "It's a beautiful day today.\n\n"
            "This sentence has no errors."
        )
        corrected_path = Path(f.name)

    # Create root window
    root = ctk.CTk()
    root.withdraw()  # Hide root window

    # Show diff viewer
    DiffViewerWindow(root, original_path, corrected_path)

    root.mainloop()

    # Cleanup
    original_path.unlink()
    corrected_path.unlink()


def test_both():
    """Test both components together."""
    # Create sample files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            "# Sample Document\n\n"
            "The quick brown fox jump over the lazy dog.\n\n"
            "Its a beautifull day today."
        )
        original_path = Path(f.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            "# Sample Document\n\n"
            "The quick brown fox jumps over the lazy dog.\n\n"
            "It's a beautiful day today."
        )
        corrected_path = Path(f.name)

    # Create sample statistics
    stats = CorrectionStats.from_pipeline_output(
        output_path=corrected_path,
        total_changes=3,
        processing_time=2.5,
        filters_applied=["GRMRV3GrammarFilter"],
    )

    # Create root window
    root = ctk.CTk()
    root.withdraw()  # Hide root window

    # Define callback to open diff viewer
    def open_diff():
        DiffViewerWindow(root, original_path, corrected_path)

    # Show success dialog first
    SuccessDialog(
        parent=root,
        output_path=corrected_path,
        stats=stats,
        on_view_diff_callback=open_diff,
    )

    root.mainloop()

    # Cleanup
    original_path.unlink()
    corrected_path.unlink()


if __name__ == "__main__":
    print("Testing Success Dialog and Diff Viewer...")
    print("\nTest options:")
    print("1. Success Dialog only")
    print("2. Diff Viewer only")
    print("3. Both (integrated workflow)")

    choice = input("\nEnter choice (1-3): ").strip()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    if choice == "1":
        test_success_dialog()
    elif choice == "2":
        test_diff_viewer()
    elif choice == "3":
        test_both()
    else:
        print("Testing integrated workflow (default)")
        test_both()

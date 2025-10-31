"""
Success Dialog - Custom dialog showing correction statistics and diff viewer access.

This dialog appears after successful pipeline completion and provides:
- Correction summary statistics
- Quick access to output file
- Button to launch detailed diff viewer
"""

from pathlib import Path

import customtkinter as ctk


class SuccessDialog:
    """
    Custom success dialog with correction statistics.

    Shows a summary of corrections made and provides buttons to:
    - View full diff (launches DiffViewer window)
    - Open output file in system editor
    - Close dialog
    """

    def __init__(
        self,
        parent,
        output_path: Path,
        stats: dict,
        on_view_diff_callback=None,
        on_open_output_callback=None,
    ):
        """
        Initialize success dialog.

        Args:
            parent: Parent window (CTk or CTkToplevel)
            output_path: Path to corrected output file
            stats: Statistics dictionary from CorrectionStats
            on_view_diff_callback: Callback when "View Full Diff" clicked
            on_open_output_callback: Callback when "Open Output" clicked
        """
        self.parent = parent
        self.output_path = output_path
        self.stats = stats
        self.on_view_diff = on_view_diff_callback
        self.on_open_output = on_open_output_callback

        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("✅ Processing Complete")
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)

        # Center on parent
        self.dialog.transient(parent)
        self.dialog.grab_set()  # Make modal

        # Build UI
        self._build_ui()

        # Focus dialog
        self.dialog.focus()

    def _build_ui(self):
        """Build dialog UI components."""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header with icon
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        success_label = ctk.CTkLabel(
            header_frame,
            text="✅ Processing Complete!",
            font=("", 20, "bold"),
            text_color="#4CAF50",  # Green
        )
        success_label.pack()

        # Output file info
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=(0, 15))

        file_label = ctk.CTkLabel(file_frame, text="📄 Output File", font=("", 12, "bold"))
        file_label.pack(anchor="w", padx=15, pady=(10, 5))

        output_text = ctk.CTkLabel(
            file_frame,
            text=str(self.output_path),
            font=("", 10),
            text_color="gray70",
            wraplength=440,
            anchor="w",
            justify="left",
        )
        output_text.pack(anchor="w", padx=15, pady=(0, 10))

        # Statistics display
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill="both", expand=True, pady=(0, 15))

        stats_label = ctk.CTkLabel(stats_frame, text="📊 Correction Summary", font=("", 12, "bold"))
        stats_label.pack(anchor="w", padx=15, pady=(10, 10))

        # Format statistics
        stats_text = self._format_stats_for_display()

        stats_display = ctk.CTkTextbox(
            stats_frame,
            font=("", 11),
            height=150,
            fg_color="gray20",
            wrap="word",
        )
        stats_display.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        stats_display.insert("1.0", stats_text)
        stats_display.configure(state="disabled")  # Read-only

        # Button row
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        # View Full Diff button (primary action)
        view_diff_btn = ctk.CTkButton(
            button_frame,
            text="🔍 View Full Diff",
            command=self._on_view_diff_clicked,
            width=140,
            height=36,
            font=("", 12, "bold"),
            fg_color="#2196F3",  # Blue
            hover_color="#1976D2",
        )
        view_diff_btn.pack(side="left", padx=(0, 8))

        # Open Output button
        open_btn = ctk.CTkButton(
            button_frame,
            text="📂 Open Output",
            command=self._on_open_output_clicked,
            width=120,
            height=36,
            font=("", 11),
        )
        open_btn.pack(side="left", padx=(0, 8))

        # Close button
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.dialog.destroy,
            width=80,
            height=36,
            font=("", 11),
            fg_color="gray40",
            hover_color="gray30",
        )
        close_btn.pack(side="left")

        # Keyboard shortcuts
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())
        self.dialog.bind("<Return>", lambda e: self._on_view_diff_clicked())

    def _format_stats_for_display(self) -> str:
        """
        Format statistics for display in dialog.

        Returns:
            Formatted multi-line string
        """
        lines = []

        # Total changes
        total = self.stats.get("total_changes", 0)
        lines.append(f"  • Total changes: {total}")

        # Processing time
        time_sec = self.stats.get("processing_time", 0.0)
        if time_sec > 0:
            if time_sec < 60:
                time_str = f"{time_sec:.1f} seconds"
            else:
                minutes = int(time_sec // 60)
                seconds = int(time_sec % 60)
                time_str = f"{minutes}m {seconds}s"
            lines.append(f"  • Processing time: {time_str}")

        # Output size
        output_size = self.stats.get("output_size_formatted", "")
        if output_size:
            lines.append(f"  • Output size: {output_size}")

        # Filters applied
        filters = self.stats.get("filters_applied", [])
        if filters:
            lines.append("")
            lines.append("  Filters applied:")
            for filter_name in filters:
                # Clean up filter names
                display_name = filter_name.replace("Filter", "").replace("_", " ").title()
                lines.append(f"    ✓ {display_name}")

        # Add helpful tip
        if total > 0:
            lines.append("")
            lines.append("💡 Tip: Click 'View Full Diff' to see all changes in detail.")

        return "\n".join(lines)

    def _on_view_diff_clicked(self):
        """Handle View Full Diff button click."""
        if self.on_view_diff:
            self.on_view_diff()
        # Keep dialog open so user can come back to it

    def _on_open_output_clicked(self):
        """Handle Open Output button click."""
        if self.on_open_output:
            self.on_open_output()
        else:
            # Default: open file in system editor
            import os
            import platform

            # Ensure output_path is a string
            path_str = str(self.output_path)

            if platform.system() == "Windows":
                os.startfile(path_str)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{path_str}"')
            else:  # Linux
                os.system(f'xdg-open "{path_str}"')

"""
Diff Viewer - GitHub-style unified diff viewer for correction review.

Displays paragraph-level differences with color coding and navigation.
"""

from pathlib import Path

import customtkinter as ctk

from satcn.gui.components.diff_engine import DiffBlock, DiffEngine


class DiffViewerWindow:
    """
    Diff viewer window showing before/after changes.

    Features:
    - Scrollable unified diff display
    - Color-coded changes (red=removed, green=added)
    - Navigation controls (Previous/Next change)
    - Export diff to text file
    - Keyboard shortcuts
    """

    def __init__(self, parent, original_path: Path, corrected_path: Path):
        """
        Initialize diff viewer window.

        Args:
            parent: Parent window (CTk or CTkToplevel)
            original_path: Path to original file
            corrected_path: Path to corrected file
        """
        self.parent = parent
        self.original_path = original_path
        self.corrected_path = corrected_path
        self.diff_blocks: list[DiffBlock] = []
        self.current_block_index = 0

        # Create window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("SATCN Pipeline - Corrections Diff")
        self.window.geometry("1000x750")

        # Build UI
        self._build_ui()

        # Load and display diff
        self._load_diff()

        # Focus window
        self.window.focus()

    def _build_ui(self):
        """Build diff viewer UI."""
        # Header
        header_frame = ctk.CTkFrame(self.window)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📝 Text Corrections Diff",
            font=("", 16, "bold"),
        )
        title_label.pack(side="left", padx=10)

        # File info
        file_info = f"{self.original_path.name} → {self.corrected_path.name}"
        file_label = ctk.CTkLabel(
            header_frame,
            text=file_info,
            font=("", 11),
            text_color="gray70",
        )
        file_label.pack(side="left", padx=(20, 0))

        # Diff display (scrollable)
        self.diff_frame = ctk.CTkScrollableFrame(self.window)
        self.diff_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Controls footer
        controls_frame = ctk.CTkFrame(self.window)
        controls_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Navigation buttons
        nav_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        nav_frame.pack(side="left")

        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀ Previous",
            command=self._go_to_previous,
            width=100,
            height=32,
        )
        self.prev_btn.pack(side="left", padx=(0, 8))

        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="Next ▶",
            command=self._go_to_next,
            width=100,
            height=32,
        )
        self.next_btn.pack(side="left")

        # Change counter
        self.counter_label = ctk.CTkLabel(
            nav_frame,
            text="No changes",
            font=("", 11),
            text_color="gray70",
        )
        self.counter_label.pack(side="left", padx=(15, 0))

        # Export and close buttons
        action_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        action_frame.pack(side="right")

        export_btn = ctk.CTkButton(
            action_frame,
            text="💾 Export Diff",
            command=self._export_diff,
            width=110,
            height=32,
        )
        export_btn.pack(side="left", padx=(0, 8))

        close_btn = ctk.CTkButton(
            action_frame,
            text="Close",
            command=self.window.destroy,
            width=80,
            height=32,
            fg_color="gray40",
            hover_color="gray30",
        )
        close_btn.pack(side="left")

        # Keyboard shortcuts
        self.window.bind("<Escape>", lambda e: self.window.destroy())
        self.window.bind("<Left>", lambda e: self._go_to_previous())
        self.window.bind("<Right>", lambda e: self._go_to_next())
        self.window.bind("<Up>", lambda e: self._go_to_previous())
        self.window.bind("<Down>", lambda e: self._go_to_next())

    def _load_diff(self):
        """Load and display diff blocks."""
        try:
            # Compute diffs using DiffEngine
            self.diff_blocks = DiffEngine.compute_paragraph_diffs(
                self.original_path, self.corrected_path
            )

            if not self.diff_blocks:
                # No changes detected
                self._show_no_changes_message()
            else:
                # Render all diff blocks
                for block in self.diff_blocks:
                    self._render_diff_block(block)

                # Update navigation state
                self._update_navigation()

        except Exception as e:
            self._show_error_message(str(e))

    def _render_diff_block(self, block: DiffBlock):
        """
        Render a single diff block with color coding.

        Args:
            block: DiffBlock object to render
        """
        # Block container
        block_frame = ctk.CTkFrame(self.diff_frame)
        block_frame.pack(fill="x", pady=8)

        # Header with paragraph number
        header = ctk.CTkLabel(
            block_frame,
            text=f"Paragraph {block.paragraph_number} (Line {block.line_number})",
            font=("", 11, "bold"),
            anchor="w",
        )
        header.pack(fill="x", padx=12, pady=(10, 8))

        # Original text (removed - red background)
        if block.change_type in ("modified", "deleted"):
            original_box = ctk.CTkTextbox(
                block_frame,
                height=max(40, min(100, len(block.original_text) // 2)),
                fg_color="#3d1f1f",  # Dark red
                text_color="#ff9999",  # Light red text
                font=("Consolas", 10),
                wrap="word",
            )
            original_box.pack(fill="x", padx=12, pady=(0, 4))
            original_box.insert("1.0", f"− {block.original_text}")
            original_box.configure(state="disabled")

        # Corrected text (added - green background)
        if block.change_type in ("modified", "added"):
            corrected_box = ctk.CTkTextbox(
                block_frame,
                height=max(40, min(100, len(block.corrected_text) // 2)),
                fg_color="#1f3d1f",  # Dark green
                text_color="#99ff99",  # Light green text
                font=("Consolas", 10),
                wrap="word",
            )
            corrected_box.pack(fill="x", padx=12, pady=(0, 10))
            corrected_box.insert("1.0", f"+ {block.corrected_text}")
            corrected_box.configure(state="disabled")

    def _show_no_changes_message(self):
        """Display message when no changes were detected."""
        message_frame = ctk.CTkFrame(self.diff_frame)
        message_frame.pack(fill="both", expand=True, padx=20, pady=50)

        icon_label = ctk.CTkLabel(
            message_frame,
            text="✓",
            font=("", 48),
            text_color="#4CAF50",
        )
        icon_label.pack(pady=(20, 10))

        message_label = ctk.CTkLabel(
            message_frame,
            text="No changes detected",
            font=("", 16, "bold"),
        )
        message_label.pack(pady=(0, 5))

        detail_label = ctk.CTkLabel(
            message_frame,
            text="The original and corrected files are identical.",
            font=("", 12),
            text_color="gray70",
        )
        detail_label.pack(pady=(0, 20))

        # Disable navigation
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")

    def _show_error_message(self, error: str):
        """
        Display error message.

        Args:
            error: Error message to display
        """
        message_frame = ctk.CTkFrame(self.diff_frame)
        message_frame.pack(fill="both", expand=True, padx=20, pady=50)

        icon_label = ctk.CTkLabel(
            message_frame,
            text="⚠️",
            font=("", 48),
        )
        icon_label.pack(pady=(20, 10))

        message_label = ctk.CTkLabel(
            message_frame,
            text="Error loading diff",
            font=("", 16, "bold"),
        )
        message_label.pack(pady=(0, 5))

        detail_label = ctk.CTkLabel(
            message_frame,
            text=error,
            font=("", 11),
            text_color="gray70",
            wraplength=600,
        )
        detail_label.pack(pady=(0, 20))

        # Disable navigation
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")

    def _update_navigation(self):
        """Update navigation button states and counter."""
        total_changes = len(self.diff_blocks)

        if total_changes == 0:
            self.counter_label.configure(text="No changes")
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
        else:
            # Update counter
            self.counter_label.configure(
                text=f"{total_changes} change{'s' if total_changes != 1 else ''} found"
            )

            # Enable/disable navigation buttons
            self.prev_btn.configure(state="normal" if self.current_block_index > 0 else "disabled")
            self.next_btn.configure(
                state="normal" if self.current_block_index < total_changes - 1 else "disabled"
            )

    def _go_to_previous(self):
        """Navigate to previous change."""
        if self.current_block_index > 0:
            self.current_block_index -= 1
            self._scroll_to_current_block()
            self._update_navigation()

    def _go_to_next(self):
        """Navigate to next change."""
        if self.current_block_index < len(self.diff_blocks) - 1:
            self.current_block_index += 1
            self._scroll_to_current_block()
            self._update_navigation()

    def _scroll_to_current_block(self):
        """Scroll to currently selected block."""
        # Note: CTkScrollableFrame doesn't have easy programmatic scrolling
        # This is a simplified implementation
        # In production, you might want to use canvas.yview_moveto()
        pass

    def _export_diff(self):
        """Export diff to text file."""
        from tkinter import filedialog

        # Ask user for save location
        save_path = filedialog.asksaveasfilename(
            title="Export Diff",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*"),
            ],
            initialfile=f"{self.original_path.stem}_diff.txt",
        )

        if save_path:
            try:
                # Export using DiffEngine
                diff_text = DiffEngine.export_diff_text(self.diff_blocks)
                Path(save_path).write_text(diff_text, encoding="utf-8")

                # Show success message
                from tkinter import messagebox

                messagebox.showinfo("Export Successful", f"Diff exported to:\n{save_path}")
            except Exception as e:
                from tkinter import messagebox

                messagebox.showerror("Export Failed", f"Error exporting diff:\n{e}")

"""
SATCN Pipeline GUI - Production interface for text correction pipeline.

This is the main GUI that exposes all CLI functionality with a modern,
user-friendly interface built with CustomTkinter.
"""

import math
import queue
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from satcn.core.pipeline_runner import PipelineRunner
from satcn.gui.components.config import PipelineConfig
from satcn.gui.components.correction_stats import CorrectionStats
from satcn.gui.components.tooltip import add_tooltip
from satcn.gui.diff_viewer import DiffViewerWindow
from satcn.gui.success_dialog import SuccessDialog

# Constants
SUPPORTED_FORMATS = {".txt", ".md", ".epub"}
WORDS_PER_PAGE = 300
DEFAULT_WINDOW_SIZE = "1000x650"  # Optimized for compact layout
MIN_WINDOW_WIDTH = 900
MIN_WINDOW_HEIGHT = 600  # Taller minimum for log visibility


class SATCNPipelineGUI:
    """
    Main GUI application for SATCN pipeline.

    Provides a graphical interface for:
    - File selection and validation
    - Grammar engine selection (LanguageTool, GRMR-V3, T5, None)
    - Pipeline options configuration
    - Real-time processing feedback
    - Output logging and progress tracking
    """

    def __init__(self):
        """Initialize the GUI application."""
        # Configuration
        self.config = PipelineConfig.load(PipelineConfig.get_config_path())

        # Processing state
        self.processing = False
        self.process_thread: threading.Thread | None = None
        self.cancel_flag = False
        self.output_queue: queue.Queue = queue.Queue()

        # File statistics
        self.file_stats: dict | None = None

        # Initialize CustomTkinter
        ctk.set_appearance_mode("dark")  # "dark", "light", or "system"
        ctk.set_default_color_theme("blue")  # "blue", "dark-blue", "green"

        # Create main window
        self.root = ctk.CTk()
        self.root.title("SATCN Pipeline - Text Correction for TTS")

        # Detect screen size and adjust window accordingly
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Compact layout - use more horizontal space, less vertical
        target_height = min(int(screen_height * 0.75), 650)
        target_width = min(1000, int(screen_width * 0.6))

        self.root.geometry(f"{target_width}x{target_height}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Add window icon if available (optional)
        try:
            # You can add an icon later: self.root.iconbitmap("path/to/icon.ico")
            pass
        except Exception:
            pass

        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Build UI
        self._build_ui()

        # Load previously selected file if exists
        if self.config.input_file and self.config.input_file.exists():
            self._load_file_stats()

        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_ui(self):
        """Construct the complete UI layout - Optimized compact design."""
        # Main container without scrollable frame (no scrolling needed)
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Let log section expand

        # TOP: File selection + Run/Cancel buttons (single row)
        self._build_header_section(main_frame, 0)

        # MIDDLE: Options in horizontal layout (grammar + pipeline side-by-side)
        self._build_options_horizontal(main_frame, 1)

        # BOTTOM: Output log (expandable)
        self._build_output_section(main_frame, 2)

    def _build_header_section(self, parent, row):
        """Build compact header: file selection + stats + run buttons."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        frame.columnconfigure(1, weight=1)

        # Row 0: File selector
        label = ctk.CTkLabel(frame, text="📁 Input File:", font=("", 12, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))

        self.file_path_var = ctk.StringVar(
            value=str(self.config.input_file) if self.config.input_file else "No file selected"
        )
        self.file_path_label = ctk.CTkLabel(
            frame, textvariable=self.file_path_var, anchor="w", text_color="gray70"
        )
        self.file_path_label.grid(row=0, column=1, sticky="ew", padx=8, pady=(8, 4))

        browse_btn = ctk.CTkButton(frame, text="Browse...", command=self._browse_file, width=100)
        browse_btn.grid(row=0, column=2, padx=(0, 10), pady=(8, 4))

        # Row 1: File stats (compact)
        stats_label = ctk.CTkLabel(frame, text="📊 Stats:", font=("", 11))
        stats_label.grid(row=1, column=0, sticky="w", padx=10, pady=4)

        self.stats_text = ctk.StringVar(value="No file loaded")
        self.stats_label = ctk.CTkLabel(
            frame, textvariable=self.stats_text, anchor="w", text_color="gray70", font=("", 10)
        )
        self.stats_label.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        # Row 2: Run controls
        controls_frame = ctk.CTkFrame(frame, fg_color="transparent")
        controls_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(4, 8))
        controls_frame.columnconfigure(2, weight=1)

        self.run_btn = ctk.CTkButton(
            controls_frame,
            text="▶️  Run Pipeline",
            command=self._run_pipeline,
            width=140,
            height=36,
            font=("", 13, "bold"),
        )
        self.run_btn.grid(row=0, column=0, padx=(0, 8))

        self.cancel_btn = ctk.CTkButton(
            controls_frame,
            text="⏹️ Cancel",
            command=self._cancel_pipeline,
            width=100,
            height=36,
            state="disabled",
        )
        self.cancel_btn.grid(row=0, column=1, padx=(0, 12))

        # Progress bar (inline)
        self.progress = ctk.CTkProgressBar(controls_frame, mode="indeterminate", height=12)
        self.progress.grid(row=0, column=2, sticky="ew", padx=(0, 12))
        self.progress.set(0)

        # Status label
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            controls_frame, textvariable=self.status_var, text_color="gray70", font=("", 10)
        )
        self.status_label.grid(row=0, column=3, sticky="e")

    def _build_options_horizontal(self, parent, row):
        """Build options section with side-by-side layout (grammar + pipeline)."""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        # LEFT: Grammar engine selection (compact)
        grammar_frame = ctk.CTkFrame(container)
        grammar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        label = ctk.CTkLabel(grammar_frame, text="⚙️  Grammar Engine", font=("", 12, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 6))

        self.engine_var = ctk.StringVar(value=self.config.grammar_engine)

        # Compact radio buttons with shorter labels
        engines = [
            ("languagetool", "LanguageTool", "Rule-based grammar checker (slow)"),
            ("grmr-v3", "GRMR-V3 (Recommended)", "GPU-accelerated, best quality"),
            ("t5", "T5 Transformer", "Experimental ML model"),
            ("none", "None", "Skip grammar correction"),
        ]

        self.engine_radios = {}
        for i, (value, text, tooltip_text) in enumerate(engines, start=1):
            radio = ctk.CTkRadioButton(
                grammar_frame,
                text=text,
                variable=self.engine_var,
                value=value,
                command=self._on_engine_change,
                font=("", 11),
            )
            radio.grid(row=i, column=0, sticky="w", padx=20, pady=3)
            self.engine_radios[value] = radio
            add_tooltip(radio, tooltip_text)

        # Mode dropdown (compact)
        mode_frame = ctk.CTkFrame(grammar_frame, fg_color="transparent")
        mode_frame.grid(row=len(engines) + 1, column=0, sticky="ew", padx=20, pady=(6, 8))

        mode_label = ctk.CTkLabel(mode_frame, text="Mode:", font=("", 11))
        mode_label.grid(row=0, column=0, sticky="w", padx=(0, 6))

        self.mode_var = ctk.StringVar(value=self.config.active_mode)
        self.mode_dropdown = ctk.CTkOptionMenu(
            mode_frame,
            variable=self.mode_var,
            values=["replace", "hybrid", "supplement"],
            width=130,
            font=("", 10),
        )
        self.mode_dropdown.grid(row=0, column=1, sticky="w")
        add_tooltip(
            self.mode_dropdown,
            "replace: Grammar model only\n"
            "hybrid: Grammar + spell-check + cleanup\n"
            "supplement: Rules first, then grammar",
        )

        # RIGHT: Pipeline options (compact)
        options_frame = ctk.CTkFrame(container)
        options_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        label = ctk.CTkLabel(options_frame, text="🔧 Pipeline Options", font=("", 12, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 6))

        # Fail-fast checkbox
        self.fail_fast_var = ctk.BooleanVar(value=self.config.fail_fast)
        fail_fast_cb = ctk.CTkCheckBox(
            options_frame,
            text="Fail fast on errors",
            variable=self.fail_fast_var,
            font=("", 11),
        )
        fail_fast_cb.grid(row=1, column=0, sticky="w", padx=20, pady=(6, 4))
        add_tooltip(
            fail_fast_cb,
            "Stop immediately on first filter failure.\n"
            "If disabled, continue processing remaining filters.",
        )

        # Advanced settings placeholder (much more compact)
        advanced_label = ctk.CTkLabel(
            options_frame,
            text="⚡ Advanced Settings",
            text_color="gray50",
            font=("", 11, "bold"),
        )
        advanced_label.grid(row=2, column=0, sticky="w", padx=20, pady=(8, 4))

        advanced_frame = ctk.CTkFrame(options_frame, fg_color="gray20")
        advanced_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 8))

        placeholders = [
            "GPU device selection",
            "Model temperature",
            "Logging verbosity",
            "Custom output path",
        ]

        for i, text in enumerate(placeholders):
            placeholder_label = ctk.CTkLabel(
                advanced_frame, text=f"• {text}", text_color="gray40", font=("", 9), anchor="w"
            )
            placeholder_label.grid(row=i, column=0, sticky="w", padx=8, pady=1)

        # Update mode dropdown state
        self._on_engine_change()

    def _build_output_section(self, parent, row):
        """Build output log section (expandable)."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Label (more compact)
        label = ctk.CTkLabel(frame, text="📝 Output Log", font=("", 12, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 6))

        # Output text area (takes all remaining space)
        self.output_text = ctk.CTkTextbox(
            frame,
            wrap="word",
            font=("Consolas", 10),
        )
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for common actions."""
        # Ctrl+O: Open file
        self.root.bind("<Control-o>", lambda e: self._browse_file())
        self.root.bind("<Control-O>", lambda e: self._browse_file())

        # Ctrl+R: Run pipeline
        self.root.bind(
            "<Control-r>", lambda e: self._run_pipeline() if not self.processing else None
        )
        self.root.bind(
            "<Control-R>", lambda e: self._run_pipeline() if not self.processing else None
        )

        # Escape: Cancel pipeline
        self.root.bind("<Escape>", lambda e: self._cancel_pipeline() if self.processing else None)

        # Ctrl+Q: Quit
        self.root.bind("<Control-q>", lambda e: self._on_closing())
        self.root.bind("<Control-Q>", lambda e: self._on_closing())

    # Event handlers

    def _browse_file(self):
        """Handle Browse button click."""
        filepath = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[
                ("Supported formats", "*.txt *.md *.epub"),
                ("Markdown files", "*.md"),
                ("EPUB files", "*.epub"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )

        if filepath:
            self.config.input_file = Path(filepath)
            self.file_path_var.set(str(filepath))
            self._load_file_stats()
            self._save_config()

    def _load_file_stats(self):
        """Load and display statistics for the selected file."""
        if not self.config.input_file or not self.config.input_file.exists():
            return

        path = self.config.input_file

        # Read file content
        try:
            if path.suffix == ".epub":
                # For EPUB, we'd need to parse it - simplified for now
                size = path.stat().st_size
                self.stats_text.set(
                    f"Size: {self._format_size(size)} | Format: EPUB\n"
                    f"Note: Word count analysis requires processing"
                )
            else:
                # Text/Markdown files
                text = path.read_text(encoding="utf-8", errors="ignore")
                words = text.split()
                word_count = len(words)
                pages = max(1, math.ceil(word_count / WORDS_PER_PAGE))
                size = path.stat().st_size
                lines = text.count("\n") + 1

                # Estimate processing time (rough)
                est_time_base = word_count * 0.005  # ~200 wps base
                est_time_grmr = word_count * 0.0006  # 1587 wps with GRMR-V3

                est_time = est_time_grmr if self.config.use_grmr else est_time_base

                self.stats_text.set(
                    f"Size: {self._format_size(size)} | Words: {word_count:,} | Lines: {lines:,}\n"
                    f"Estimated pages: {pages} | Est. processing time: ~{int(est_time)}s"
                )
        except Exception as e:
            self.stats_text.set(f"Error reading file: {e}")

    def _on_engine_change(self):
        """Handle grammar engine radio button change."""
        engine = self.engine_var.get()

        # Enable/disable mode dropdown based on engine
        if engine in ("grmr-v3", "t5"):
            self.mode_dropdown.configure(state="normal")
        else:
            self.mode_dropdown.configure(state="disabled")

        # Update processing time estimate (only if stats section exists)
        if hasattr(self, "stats_text"):
            self._load_file_stats()

    def _run_pipeline(self):
        """Handle Run Pipeline button click."""
        # Validate configuration
        errors = self.config.validate()
        if errors:
            messagebox.showerror("Configuration Error", "\n".join(errors))
            return

        # Update config from UI state
        self._sync_config_from_ui()

        # Save config
        self._save_config()

        # Disable UI elements
        self._set_processing_state(True)

        # Clear output log
        self.output_text.delete("1.0", "end")
        self._log("Starting SATCN pipeline...")
        self._log(f"Input: {self.config.input_file}")
        self._log(f"Grammar engine: {self.config.grammar_engine}")

        # Start processing thread
        self.cancel_flag = False
        self.process_thread = threading.Thread(target=self._process_file, daemon=True)
        self.process_thread.start()

        # Start queue monitor
        self.root.after(100, self._check_queue)

    def _cancel_pipeline(self):
        """Handle Cancel button click."""
        self.cancel_flag = True
        self._log("Cancellation requested...")
        self.status_var.set("Cancelling...")

    def _process_file(self):
        """Run pipeline in background thread."""
        import time

        start_time = time.time()

        try:
            # Create PipelineRunner
            runner = PipelineRunner(
                input_filepath=str(self.config.input_file),
                fail_fast=self.config.fail_fast,
                use_grmr=self.config.use_grmr,
                grmr_mode=self.config.grmr_mode if self.config.use_grmr else "replace",
                use_t5=self.config.use_t5,
                t5_mode=self.config.t5_mode if self.config.use_t5 else "replace",
            )

            # Run pipeline (this will take time)
            output_path = runner.run()
            end_time = time.time()

            if self.cancel_flag:
                self.output_queue.put(("status", "Cancelled by user"))
            else:
                # Gather statistics
                processing_time = end_time - start_time

                # Build filter list from config
                filters_applied = []
                if self.config.grammar_engine != "none":
                    if self.config.use_grmr:
                        filters_applied.append("GRMRV3GrammarFilter")
                    elif self.config.use_t5:
                        filters_applied.append("T5CorrectionFilter")
                    else:
                        filters_applied.append("GrammarFilter")

                # Create stats dict
                try:
                    stats = CorrectionStats.from_pipeline_output(
                        output_path=Path(output_path),
                        total_changes=0,  # TODO: Get from runner if available
                        processing_time=processing_time,
                        filters_applied=filters_applied,
                    )
                except Exception as stats_error:
                    # If stats creation fails, use minimal stats
                    print(f"Warning: Could not create stats: {stats_error}")
                    stats = {
                        "output_path": str(output_path),
                        "total_changes": 0,
                        "processing_time": processing_time,
                        "filters_applied": filters_applied,
                    }

                self.output_queue.put(("success", (output_path, stats)))

        except Exception as e:
            import traceback

            error_details = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            self.output_queue.put(("error", error_details))

    def _check_queue(self):
        """Check output queue for messages from processing thread."""
        try:
            while True:
                msg_type, msg_data = self.output_queue.get_nowait()

                if msg_type == "log":
                    self._log(msg_data)
                elif msg_type == "status":
                    self.status_var.set(msg_data)
                elif msg_type == "success":
                    # Unpack tuple - handle both old and new formats
                    if isinstance(msg_data, tuple):
                        output_path, stats = msg_data
                    else:
                        # Fallback for old format (just output_path string)
                        output_path = msg_data
                        stats = CorrectionStats.from_pipeline_output(
                            output_path=Path(output_path),
                            total_changes=0,
                            processing_time=0.0,
                            filters_applied=[],
                        )

                    self._log("\n✅ Pipeline completed successfully!")
                    self._log(f"Output: {output_path}")
                    self.status_var.set("Completed")
                    self._set_processing_state(False)

                    # Show custom success dialog with diff button
                    self._show_success_dialog(output_path, stats)
                    return  # Stop checking
                elif msg_type == "error":
                    self._log(f"\n❌ Error: {msg_data}")
                    self.status_var.set("Error")
                    self._set_processing_state(False)
                    messagebox.showerror("Processing Error", msg_data)
                    return  # Stop checking

        except queue.Empty:
            pass

        # Continue checking if still processing
        if self.processing:
            self.root.after(100, self._check_queue)

    def _set_processing_state(self, processing: bool):
        """Enable/disable UI elements based on processing state."""
        self.processing = processing

        if processing:
            self.run_btn.configure(state="disabled")
            self.cancel_btn.configure(state="normal")
            self.progress.start()
            self.status_var.set("Processing...")
        else:
            self.run_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
            self.progress.stop()
            self.progress.set(0)

    def _log(self, message: str):
        """Append message to output log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert("end", f"[{timestamp}] {message}\n")
        self.output_text.see("end")  # Auto-scroll

    def _sync_config_from_ui(self):
        """Sync configuration from UI state."""
        self.config.grammar_engine = self.engine_var.get()
        self.config.fail_fast = self.fail_fast_var.get()

        # Update mode based on engine
        mode = self.mode_var.get()
        if self.config.use_grmr:
            self.config.grmr_mode = mode
        elif self.config.use_t5:
            self.config.t5_mode = mode

    def _save_config(self):
        """Save configuration to disk."""
        try:
            self.config.save(PipelineConfig.get_config_path())
        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    def _show_success_dialog(self, output_path: str, stats: dict):
        """
        Show custom success dialog with correction statistics.

        Args:
            output_path: Path to corrected output file
            stats: Statistics dictionary from CorrectionStats
        """
        SuccessDialog(
            parent=self.root,
            output_path=Path(output_path),
            stats=stats,
            on_view_diff_callback=lambda: self._open_diff_viewer(
                self.config.input_file, Path(output_path)
            ),
            on_open_output_callback=lambda: self._open_output_file(output_path),
        )

    def _open_diff_viewer(self, original_path: Path, corrected_path: Path):
        """
        Open diff viewer window.

        Args:
            original_path: Path to original file
            corrected_path: Path to corrected file
        """
        DiffViewerWindow(self.root, original_path, corrected_path)

    def _open_output_file(self, output_path: str):
        """
        Open output file in system editor.

        Args:
            output_path: Path to output file
        """
        import os
        import platform

        try:
            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{output_path}"')
            else:  # Linux
                os.system(f'xdg-open "{output_path}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def _on_closing(self):
        """Handle window close event."""
        if self.processing:
            if messagebox.askokcancel(
                "Pipeline Running", "Pipeline is still running. Cancel and exit?"
            ):
                self.cancel_flag = True
                self.root.destroy()
        else:
            self.root.destroy()

    @staticmethod
    def _format_size(bytes: int) -> str:
        """Format byte size in human-readable format."""
        if bytes <= 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB"]
        power = min(int(math.log(bytes, 1024)), len(units) - 1)
        return f"{bytes / (1024 ** power):.2f} {units[power]}"

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()


def main():
    """Entry point for SATCN GUI."""
    app = SATCNPipelineGUI()
    app.run()


if __name__ == "__main__":
    main()

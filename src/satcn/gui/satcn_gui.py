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
from satcn.gui.components.tooltip import add_tooltip

# Constants
SUPPORTED_FORMATS = {".txt", ".md", ".epub"}
WORDS_PER_PAGE = 300
DEFAULT_WINDOW_SIZE = "950x750"  # Reduced height for high-DPI displays
MIN_WINDOW_WIDTH = 700
MIN_WINDOW_HEIGHT = 500  # Smaller minimum for 225% scaling


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

        # For high-DPI displays (225% scaling), use smaller window
        # Calculate 80% of screen height, max 800px
        target_height = min(int(screen_height * 0.8), 800)
        target_width = min(950, int(screen_width * 0.5))

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
        """Construct the complete UI layout."""
        # Create scrollable frame to handle content overflow on high-DPI displays
        # This ensures all content is accessible even if window is smaller than content
        scrollable_frame = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)
        scrollable_frame.columnconfigure(0, weight=1)

        # Use scrollable frame as parent for all content
        main_frame = scrollable_frame

        # Build sections top-to-bottom
        row = 0

        # 1. File selection section
        self._build_file_section(main_frame, row)
        row += 1

        # 2. Grammar engine selection
        self._build_grammar_section(main_frame, row)
        row += 1

        # 3. Pipeline options
        self._build_options_section(main_frame, row)
        row += 1

        # 4. File statistics display
        self._build_stats_section(main_frame, row)
        row += 1

        # 5. Run/Cancel buttons + progress
        self._build_controls_section(main_frame, row)
        row += 1

        # 6. Output log
        self._build_output_section(main_frame, row)
        main_frame.rowconfigure(row, weight=1)  # Let log expand

    def _build_file_section(self, parent, row):
        """Build file selection section."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(1, weight=1)

        # Label
        label = ctk.CTkLabel(frame, text="📁 Input File", font=("", 14, "bold"))
        label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))

        # File path display
        self.file_path_var = ctk.StringVar(
            value=str(self.config.input_file) if self.config.input_file else "No file selected"
        )
        self.file_path_label = ctk.CTkLabel(
            frame, textvariable=self.file_path_var, anchor="w", text_color="gray70"
        )
        self.file_path_label.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))

        # Browse button
        browse_btn = ctk.CTkButton(frame, text="Browse...", command=self._browse_file, width=120)
        browse_btn.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))

    def _build_grammar_section(self, parent, row):
        """Build grammar engine selection section."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))

        # Label
        label = ctk.CTkLabel(frame, text="⚙️  Grammar Correction Engine", font=("", 14, "bold"))
        label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 10))

        # Radio button variable
        self.engine_var = ctk.StringVar(value=self.config.grammar_engine)

        # Radio buttons (mutually exclusive)
        engines = [
            (
                "languagetool",
                "LanguageTool (rule-based, slow)",
                "Default rule-based grammar checker",
            ),
            ("grmr-v3", "GRMR-V3 GGUF (GPU-accelerated, recommended)", "Best quality, uses GPU"),
            ("t5", "T5 Transformer (experimental)", "Experimental ML model"),
            ("none", "None (skip grammar correction)", "Only apply other filters"),
        ]

        self.engine_radios = {}
        for i, (value, text, tooltip_text) in enumerate(engines, start=1):
            radio = ctk.CTkRadioButton(
                frame,
                text=text,
                variable=self.engine_var,
                value=value,
                command=self._on_engine_change,
            )
            radio.grid(row=i, column=0, sticky="w", padx=30, pady=5)
            self.engine_radios[value] = radio
            # Add tooltip
            add_tooltip(radio, tooltip_text)

        # Mode dropdown (contextual - only for GRMR/T5)
        mode_frame = ctk.CTkFrame(frame)
        mode_frame.grid(row=len(engines) + 1, column=0, sticky="ew", padx=30, pady=(10, 15))
        mode_frame.columnconfigure(1, weight=1)

        mode_label = ctk.CTkLabel(mode_frame, text="Correction Mode:")
        mode_label.grid(row=0, column=0, sticky="w", padx=5)

        self.mode_var = ctk.StringVar(value=self.config.active_mode)
        self.mode_dropdown = ctk.CTkOptionMenu(
            mode_frame,
            variable=self.mode_var,
            values=["replace", "hybrid", "supplement"],
            width=150,
        )
        self.mode_dropdown.grid(row=0, column=1, sticky="w", padx=10)
        add_tooltip(
            self.mode_dropdown,
            "replace: Use only grammar model\n"
            "hybrid: Grammar model + spell-check + cleanup\n"
            "supplement: Rule-based first, then grammar model",
        )

        # Update mode dropdown state based on selected engine
        self._on_engine_change()

    def _build_options_section(self, parent, row):
        """Build pipeline options section."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))

        # Label
        label = ctk.CTkLabel(frame, text="🔧 Pipeline Options", font=("", 14, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 10))

        # Fail-fast checkbox
        self.fail_fast_var = ctk.BooleanVar(value=self.config.fail_fast)
        fail_fast_cb = ctk.CTkCheckBox(
            frame,
            text="Fail fast on errors (stop at first filter failure)",
            variable=self.fail_fast_var,
        )
        fail_fast_cb.grid(row=1, column=0, sticky="w", padx=30, pady=5)
        add_tooltip(
            fail_fast_cb,
            "If enabled, pipeline stops immediately when any filter fails.\n"
            "If disabled, pipeline continues processing remaining filters.",
        )

        # Advanced settings expander (grayed out - placeholder)
        advanced_label = ctk.CTkLabel(
            frame, text="⚡ Advanced Settings (coming soon)", text_color="gray50", font=("", 12)
        )
        advanced_label.grid(row=2, column=0, sticky="w", padx=30, pady=(10, 5))

        # Placeholder advanced options (disabled)
        advanced_frame = ctk.CTkFrame(frame, fg_color="gray20")
        advanced_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 10))

        placeholders = [
            "GPU device selection",
            "Model temperature adjustment",
            "Logging verbosity level",
            "Custom output path",
        ]

        for i, text in enumerate(placeholders):
            placeholder_label = ctk.CTkLabel(
                advanced_frame, text=f"  • {text}", text_color="gray40", font=("", 11)
            )
            placeholder_label.grid(row=i, column=0, sticky="w", padx=10, pady=2)

    def _build_stats_section(self, parent, row):
        """Build file statistics display section."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))

        # Label
        label = ctk.CTkLabel(frame, text="📊 File Statistics", font=("", 14, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 10))

        # Stats display (updated when file is loaded)
        self.stats_text = ctk.StringVar(value="No file loaded")
        self.stats_label = ctk.CTkLabel(
            frame, textvariable=self.stats_text, anchor="w", justify="left", text_color="gray70"
        )
        self.stats_label.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 10))

    def _build_controls_section(self, parent, row):
        """Build run/cancel buttons and progress bar."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(0, weight=1)

        # Button row
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        button_frame.columnconfigure(1, weight=1)

        # Run button
        self.run_btn = ctk.CTkButton(
            button_frame,
            text="▶️  Run Pipeline",
            command=self._run_pipeline,
            width=150,
            height=40,
            font=("", 14, "bold"),
        )
        self.run_btn.grid(row=0, column=0, padx=(0, 10))

        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel_pipeline,
            width=100,
            height=40,
            state="disabled",
        )
        self.cancel_btn.grid(row=0, column=1, sticky="w")

        # Progress bar
        self.progress = ctk.CTkProgressBar(frame, mode="indeterminate")
        self.progress.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.progress.set(0)

        # Status label
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(frame, textvariable=self.status_var, text_color="gray70")
        self.status_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))

    def _build_output_section(self, parent, row):
        """Build output log section."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="nsew", pady=(0, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Label
        label = ctk.CTkLabel(frame, text="📝 Pipeline Output Log", font=("", 14, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 10))

        # Output text area (scrollable)
        # Set height to ensure minimum visible lines (adjusts for high-DPI)
        self.output_text = ctk.CTkTextbox(
            frame,
            wrap="word",
            font=("Consolas", 10),
            height=150,  # Minimum height in pixels
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
            # TODO: Add callback mechanism to get progress updates
            output_path = runner.run()

            if self.cancel_flag:
                self.output_queue.put(("status", "Cancelled by user"))
            else:
                self.output_queue.put(("success", output_path))

        except Exception as e:
            self.output_queue.put(("error", str(e)))

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
                    self._log("\n✅ Pipeline completed successfully!")
                    self._log(f"Output: {msg_data}")
                    self.status_var.set("Completed")
                    self._set_processing_state(False)
                    messagebox.showinfo("Success", f"Processing complete!\n\nOutput: {msg_data}")
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

"""
GRMR-V3 GPU Test GUI
Standalone GUI for testing GRMR-V3 grammar correction with GPU acceleration.
"""

import math
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Optional

from satcn.core.filters.grmr_v3_filter import GRMRV3GrammarFilter

SUPPORTED_EXTENSIONS = {".txt", ".md"}
WORDS_PER_PAGE = 300


@dataclass
class FileStats:
    path: Path
    size_bytes: int
    word_count: int
    page_estimate: int
    modified_at: datetime
    char_count: int
    line_count: int

    @property
    def size_human(self) -> str:
        if self.size_bytes <= 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB"]
        power = min(int(math.log(self.size_bytes, 1024)), len(units) - 1)
        return f"{self.size_bytes / (1024 ** power):.2f} {units[power]}"


def collect_file_stats(path: Path) -> FileStats:
    """Collect statistics about a text file."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    line_count = text.count("\n") + 1
    pages = max(1, math.ceil(word_count / WORDS_PER_PAGE)) if word_count else 0
    size_bytes = path.stat().st_size
    modified_at = datetime.fromtimestamp(path.stat().st_mtime)

    return FileStats(
        path=path,
        size_bytes=size_bytes,
        word_count=word_count,
        page_estimate=pages,
        modified_at=modified_at,
        char_count=char_count,
        line_count=line_count,
    )


class GRMRV3TestGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GRMR-V3 GPU Test Utility")
        self.root.geometry("900x750")

        self.file_path = None
        self.stats = None
        self.filter = None
        self.processing = False
        self.process_thread = None
        self.cancel_flag = False

        self._create_widgets()

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Input File", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        self.file_path_var = tk.StringVar(value="No file selected")
        ttk.Label(file_frame, textvariable=self.file_path_var, width=60).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )

        ttk.Button(file_frame, text="Browse...", command=self.browse_file).grid(
            row=1, column=0, sticky="w"
        )

        # File statistics
        stats_frame = ttk.LabelFrame(main_frame, text="File Statistics", padding="10")
        stats_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        stats_frame.columnconfigure(0, weight=1)

        self.stats_text = tk.Text(stats_frame, height=6, width=80, state="disabled")
        self.stats_text.grid(row=0, column=0, sticky="ew")

        # GPU Settings section
        gpu_frame = ttk.LabelFrame(main_frame, text="GPU Settings", padding="10")
        gpu_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(gpu_frame, text="Device:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.device_var = tk.StringVar(value="cuda")
        device_combo = ttk.Combobox(
            gpu_frame,
            textvariable=self.device_var,
            values=["cuda", "cpu", "auto"],
            state="readonly",
            width=15,
        )
        device_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(gpu_frame, text="Temperature:").grid(row=0, column=2, sticky="w", padx=(20, 10))
        self.temp_var = tk.StringVar(value="0.1")
        temp_spin = ttk.Spinbox(
            gpu_frame, textvariable=self.temp_var, from_=0.1, to=1.0, increment=0.1, width=10
        )
        temp_spin.grid(row=0, column=3, sticky="w")

        ttk.Label(gpu_frame, text="Top-P:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0)
        )
        self.top_p_var = tk.StringVar(value="0.15")
        top_p_spin = ttk.Spinbox(
            gpu_frame, textvariable=self.top_p_var, from_=0.01, to=1.0, increment=0.05, width=10
        )
        top_p_spin.grid(row=1, column=1, sticky="w", pady=(5, 0))

        ttk.Label(gpu_frame, text="Max Tokens:").grid(
            row=1, column=2, sticky="w", padx=(20, 10), pady=(5, 0)
        )
        self.max_tokens_var = tk.StringVar(value="256")
        max_tokens_spin = ttk.Spinbox(
            gpu_frame, textvariable=self.max_tokens_var, from_=128, to=2048, increment=128, width=10
        )
        max_tokens_spin.grid(row=1, column=3, sticky="w", pady=(5, 0))

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)

        button_container = ttk.Frame(control_frame)
        button_container.grid(row=0, column=0)

        self.run_button = ttk.Button(
            button_container, text="Run Correction", command=self.run_correction
        )
        self.run_button.grid(row=0, column=0, padx=5)

        self.cancel_button = ttk.Button(
            button_container, text="Cancel", command=self.cancel_correction, state="disabled"
        )
        self.cancel_button.grid(row=0, column=1, padx=5)

        self.save_button = ttk.Button(
            button_container, text="Save Output", command=self.save_output, state="disabled"
        )
        self.save_button.grid(row=0, column=2, padx=5)

        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )

        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, sticky="ew")

        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Corrected Output", padding="10")
        output_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)

        self.output_text = scrolledtext.ScrolledText(
            output_frame, height=20, width=80, wrap=tk.WORD
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")

        # Status bar
        self.status_var = tk.StringVar(value="Ready - Select a file to begin")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def browse_file(self):
        """Browse for input file."""
        filepath = filedialog.askopenfilename(
            title="Select text file to correct",
            filetypes=(
                ("Text files", "*.txt *.md"),
                ("Markdown files", "*.md"),
                ("All files", "*.*"),
            ),
        )
        if not filepath:
            return

        path = Path(filepath)
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            messagebox.showerror("Unsupported file", "Please choose a .txt or .md file.")
            return

        self.file_path = path
        self.file_path_var.set(str(path.name))

        try:
            self.stats = collect_file_stats(path)
            self._display_stats(self.stats)
            self.status_var.set(f"File loaded: {path.name}")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to read the file: {exc}")
            self.file_path = None
            self.stats = None
            self._display_stats(None)

    def _display_stats(self, stats: Optional[FileStats]):
        """Display file statistics."""
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", tk.END)

        if not stats:
            self.stats_text.insert(tk.END, "No file selected.")
        else:
            # Estimate processing time based on GPU speed (~1500 wpm)
            est_seconds = max(1, int(stats.word_count / 1500))
            lines = [
                f"Path: {stats.path}",
                f"Size: {stats.size_human}",
                f"Words: {stats.word_count:,}",
                f"Characters: {stats.char_count:,}",
                f"Lines: {stats.line_count:,}",
                f"Estimated pages: {stats.page_estimate}",
                f"Est. GPU processing time: ~{est_seconds} seconds",
            ]
            self.stats_text.insert(tk.END, "\n".join(lines))

        self.stats_text.config(state="disabled")

    def run_correction(self):
        """Run grammar correction in background thread."""
        if self.processing:
            messagebox.showwarning(
                "Already running", "Please wait for the current correction to finish."
            )
            return

        if not self.file_path:
            messagebox.showwarning("No file", "Please select a file first.")
            return

        # Read input text
        try:
            input_text = self.file_path.read_text(encoding="utf-8")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to read file: {exc}")
            return

        # Clear output
        self.output_text.delete("1.0", tk.END)

        # Update UI state
        self.processing = True
        self.cancel_flag = False
        self.run_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self.save_button.config(state="disabled")
        self.progress_bar.start(10)

        # Get parameters
        device = self.device_var.get()
        try:
            temperature = float(self.temp_var.get())
            top_p = float(self.top_p_var.get())
            max_tokens = int(self.max_tokens_var.get())
        except ValueError:
            messagebox.showerror(
                "Invalid parameters", "Please check temperature, top-p, and max tokens values."
            )
            self._reset_ui()
            return

        # Start processing thread
        self.process_thread = threading.Thread(
            target=self._process_correction,
            args=(input_text, device, temperature, top_p, max_tokens),
            daemon=True,
        )
        self.process_thread.start()

        # Start monitoring thread
        self.root.after(100, self._check_thread)

    def _process_correction(
        self, text: str, device: str, temperature: float, top_p: float, max_tokens: int
    ):
        """Process correction in background thread."""
        try:
            # Update status
            self.root.after(0, lambda: self.progress_var.set("Initializing GRMR-V3 model..."))
            self.root.after(
                0, lambda: self.status_var.set("Loading model with GPU acceleration...")
            )

            # Initialize filter
            self.filter = GRMRV3GrammarFilter(
                temperature=temperature, top_p=top_p, max_new_tokens=max_tokens, device=device
            )

            if self.cancel_flag:
                return

            # Process text
            self.root.after(0, lambda: self.progress_var.set("Processing text..."))
            self.root.after(
                0, lambda: self.status_var.set("Running grammar correction with GPU...")
            )

            start_time = time.time()
            corrected = self.filter.correct_text(text)
            elapsed = time.time() - start_time

            if self.cancel_flag:
                return

            # Calculate stats
            word_count = len(text.split())
            wpm = int(word_count / elapsed) if elapsed > 0 else 0

            # Update output
            self.root.after(0, lambda: self.output_text.delete("1.0", tk.END))
            self.root.after(0, lambda: self.output_text.insert("1.0", corrected))

            # Update status
            status_msg = (
                f"✓ Complete! Processed {word_count:,} words in {elapsed:.1f}s ({wpm:,} wpm)"
            )
            self.root.after(0, lambda: self.progress_var.set(status_msg))
            self.root.after(0, lambda: self.status_var.set(f"Ready - Last run: {elapsed:.1f}s"))
            self.root.after(0, lambda: self.save_button.config(state="normal"))

        except Exception as exc:
            error_msg = f"Error during correction: {exc}"
            self.root.after(0, lambda: self.progress_var.set("❌ Error"))
            self.root.after(0, lambda: self.status_var.set(error_msg))
            self.root.after(0, lambda: messagebox.showerror("Processing Error", error_msg))

        finally:
            self.root.after(0, self._reset_ui)

    def _check_thread(self):
        """Check if processing thread is still running."""
        if self.process_thread and self.process_thread.is_alive():
            self.root.after(100, self._check_thread)
        else:
            self._reset_ui()

    def _reset_ui(self):
        """Reset UI to ready state."""
        self.processing = False
        self.run_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.progress_bar.stop()

    def cancel_correction(self):
        """Cancel the running correction."""
        self.cancel_flag = True
        self.progress_var.set("Cancelling...")
        self.status_var.set("Cancelled by user")
        self._reset_ui()

    def save_output(self):
        """Save corrected output to file."""
        output = self.output_text.get("1.0", tk.END).strip()
        if not output:
            messagebox.showwarning("No output", "No corrected text to save.")
            return

        # Suggest output filename
        if self.file_path:
            default_name = self.file_path.stem + "_corrected" + self.file_path.suffix
            initial_dir = self.file_path.parent
        else:
            default_name = "corrected.txt"
            initial_dir = Path.home()

        filepath = filedialog.asksaveasfilename(
            title="Save corrected text",
            initialdir=initial_dir,
            initialfile=default_name,
            defaultextension=".txt",
            filetypes=(
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*"),
            ),
        )

        if not filepath:
            return

        try:
            Path(filepath).write_text(output, encoding="utf-8")
            self.status_var.set(f"Saved to: {filepath}")
            messagebox.showinfo("Saved", f"Output saved to:\n{filepath}")
        except Exception as exc:
            messagebox.showerror("Save Error", f"Failed to save file: {exc}")

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = GRMRV3TestGUI()
    app.run()


if __name__ == "__main__":
    main()

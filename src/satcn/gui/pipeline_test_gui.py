"""Standalone GUI utility for manually testing the SATCN pipeline."""
from __future__ import annotations

import math
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import ebooklib  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from ebooklib import epub  # type: ignore
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


SUPPORTED_EXTENSIONS = {".txt", ".md", ".epub"}
WORDS_PER_PAGE = 300
WORDS_PER_SECOND = 140  # crude estimate used for processing time heuristics
WORDS_PER_SECOND_T5 = 15  # T5 model inference is much slower (~10x slower than regular filters)


@dataclass
class FileStats:
    path: Path
    size_bytes: int
    word_count: int
    page_estimate: int
    modified_at: datetime
    extra: Dict[str, str]

    @property
    def size_human(self) -> str:
        return human_readable_size(self.size_bytes)


def human_readable_size(size: int) -> str:
    if size <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    power = min(int(math.log(size, 1024)), len(units) - 1)
    return f"{size / (1024 ** power):.2f} {units[power]}"


def load_text_for_stats(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    # EPUB parsing
    text_chunks = []
    book = epub.read_epub(str(path))
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        for paragraph in soup.find_all("p"):
            if paragraph.get_text(strip=True):
                text_chunks.append(paragraph.get_text(strip=True))
    return "\n".join(text_chunks)


def collect_file_stats(path: Path) -> FileStats:
    text = load_text_for_stats(path)
    words = text.split()
    word_count = len(words)
    pages = max(1, math.ceil(word_count / WORDS_PER_PAGE)) if word_count else 0
    size_bytes = path.stat().st_size
    modified_at = datetime.fromtimestamp(path.stat().st_mtime)

    extra: Dict[str, str] = {}
    if word_count:
        # NOTE: This shows base estimate only. Actual time depends on filters selected.
        seconds = max(1, int(word_count / WORDS_PER_SECOND))
        extra["Estimated processing time (base)"] = f"~{seconds} seconds"
        # Add T5 estimate for reference
        seconds_t5 = max(1, int(word_count / WORDS_PER_SECOND_T5)) + 12
        extra["Estimated with T5"] = f"~{seconds_t5} seconds"
    extra["Line count"] = str(text.count("\n") + 1)

    return FileStats(
        path=path,
        size_bytes=size_bytes,
        word_count=word_count,
        page_estimate=pages,
        modified_at=modified_at,
        extra=extra,
    )


class PipelineTestGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("SATCN Pipeline Test Utility")
        self.root.geometry("760x620")

        self.file_path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Select a file to begin.")
        self.fail_fast_var = tk.BooleanVar(value=False)
        self.use_t5_var = tk.BooleanVar(value=False)
        self.t5_mode_var = tk.StringVar(value="replace")

        self._build_layout()

        self.stats: Optional[FileStats] = None
        self.output_queue: "queue.Queue[tuple[str, str]]" = queue.Queue()
        self.process_thread: Optional[threading.Thread] = None
        self.current_process: Optional[subprocess.Popen[str]] = None
        self.cancel_event = threading.Event()
        self.log_buffer: List[str] = []
        self.run_records: List[Dict[str, object]] = []
        self._current_run_start_perf: Optional[float] = None
        self._current_run_start_time: Optional[datetime] = None
        self._current_estimated_seconds: Optional[int] = None

        self._poll_output_queue()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        padding = {"padx": 12, "pady": 6}

        file_frame = ttk.LabelFrame(self.root, text="Input file")
        file_frame.pack(fill="x", padx=12, pady=12)

        entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly")
        entry.pack(side="left", fill="x", expand=True, **padding)
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.pack(side="left", **padding)

        options_frame = ttk.LabelFrame(self.root, text="Pipeline options")
        options_frame.pack(fill="x", padx=12, pady=6)

        ttk.Checkbutton(
            options_frame,
            text="Fail fast",
            variable=self.fail_fast_var,
        ).grid(row=0, column=0, sticky="w", **padding)

        ttk.Checkbutton(
            options_frame,
            text="Use T5 corrections",
            variable=self.use_t5_var,
            command=self._toggle_t5_options,
        ).grid(row=0, column=1, sticky="w", **padding)

        ttk.Label(options_frame, text="T5 mode:").grid(row=1, column=0, sticky="e", **padding)
        self.t5_mode_combo = ttk.Combobox(
            options_frame,
            textvariable=self.t5_mode_var,
            state="disabled",
            values=("replace", "hybrid", "supplement"),
        )
        self.t5_mode_combo.grid(row=1, column=1, sticky="w", **padding)

        stats_frame = ttk.LabelFrame(self.root, text="File statistics")
        stats_frame.pack(fill="both", expand=False, padx=12, pady=6)

        self.stats_text = tk.Text(stats_frame, height=8, state="disabled", wrap="word")
        self.stats_text.pack(fill="both", expand=True, padx=8, pady=8)

        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(fill="x", padx=12, pady=6)

        self.progress = ttk.Progressbar(controls_frame, mode="indeterminate")
        self.progress.pack(fill="x", expand=True, side="left", padx=(0, 12))

        self.run_button = ttk.Button(controls_frame, text="Run pipeline", command=self.run_pipeline)
        self.run_button.pack(side="left")

        self.cancel_button = ttk.Button(controls_frame, text="Cancel", command=self.cancel_pipeline, state="disabled")
        self.cancel_button.pack(side="left", padx=(12, 0))

        status_frame = ttk.LabelFrame(self.root, text="Pipeline output")
        status_frame.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        self.log_text = tk.Text(status_frame, state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=8, pady=8)

        self.status_label = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill="x", padx=12, pady=(0, 12))

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _toggle_t5_options(self) -> None:
        state = "readonly" if self.use_t5_var.get() else "disabled"
        self.t5_mode_combo.config(state=state)

    def browse_file(self) -> None:
        filepath = filedialog.askopenfilename(
            title="Select a document",
            filetypes=(
                ("Supported documents", "*.txt *.md *.epub"),
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("EPUB files", "*.epub"),
                ("All files", "*.*"),
            ),
        )
        if not filepath:
            return

        path = Path(filepath)
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            messagebox.showerror("Unsupported file", "Please choose a .txt, .md, or .epub file.")
            return

        self.file_path_var.set(str(path))
        try:
            self.stats = collect_file_stats(path)
            self._display_stats(self.stats)
            self.status_var.set("Ready to run pipeline.")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to read the file: {exc}")
            self.file_path_var.set("")
            self.stats = None
            self._display_stats(None)

    def _display_stats(self, stats: Optional[FileStats]) -> None:
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", tk.END)
        if not stats:
            self.stats_text.insert(tk.END, "No file selected.")
        else:
            lines = [
                f"Path: {stats.path}",
                f"Size: {stats.size_human}",
                f"Word count: {stats.word_count}",
                f"Estimated pages: {stats.page_estimate}",
                f"Last modified: {stats.modified_at:%Y-%m-%d %H:%M:%S}",
            ]
            for key, value in stats.extra.items():
                lines.append(f"{key}: {value}")
            self.stats_text.insert(tk.END, "\n".join(lines))
        self.stats_text.config(state="disabled")

    def run_pipeline(self) -> None:
        if self.process_thread and self.process_thread.is_alive():
            messagebox.showwarning("Pipeline running", "Please wait for the current run to finish or cancel it.")
            return

        filepath = self.file_path_var.get()
        if not filepath:
            messagebox.showerror("No file", "Please select a file first.")
            return

        path = Path(filepath)
        if not path.exists():
            messagebox.showerror("Missing file", "The selected file no longer exists.")
            return

        self.progress.start(8)
        self.cancel_event.clear()
        self.run_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self.status_var.set("Running pipeline...")
        self._append_log("Starting pipeline run...\n")

        estimated_seconds: Optional[int] = None
        if self.stats and self.stats.word_count:
            # Use slower estimate if T5 correction is enabled
            wps = WORDS_PER_SECOND_T5 if self.use_t5_var.get() else WORDS_PER_SECOND
            estimated_seconds = max(1, int(self.stats.word_count / wps))
            # Add model loading overhead for T5 (approximately 10-15 seconds)
            if self.use_t5_var.get():
                estimated_seconds += 12
            self._append_log(f"Estimated runtime: ~{estimated_seconds} seconds\n")

        self._current_run_start_perf = time.perf_counter()
        self._current_run_start_time = datetime.now()
        self._current_estimated_seconds = estimated_seconds

        self.process_thread = threading.Thread(
            target=self._execute_pipeline,
            args=(path, self._current_run_start_perf, self._current_run_start_time, estimated_seconds),
            daemon=True,
        )
        self.process_thread.start()

    def cancel_pipeline(self) -> None:
        if self.current_process is not None:
            self.cancel_event.set()
            self.current_process.terminate()
            self.output_queue.put(("status", "Cancelling pipeline..."))
        else:
            self.cancel_event.set()
            self.status_var.set("No active pipeline run.")
            self.cancel_button.config(state="disabled")

    # ------------------------------------------------------------------
    # Pipeline execution
    # ------------------------------------------------------------------
    def _execute_pipeline(
        self,
        original_path: Path,
        start_perf: Optional[float],
        start_time: Optional[datetime],
        estimated_seconds: Optional[int],
    ) -> None:
        temp_dir: Optional[Path] = None
        input_path = original_path
        txt_mode = original_path.suffix.lower() == ".txt"
        status_label = "failed"
        try:
            if txt_mode:
                temp_dir = Path(tempfile.mkdtemp(prefix="satcn_txt_"))
                temp_input = temp_dir / f"{original_path.stem}.md"
                content = original_path.read_text(encoding="utf-8", errors="ignore")
                temp_input.write_text(content, encoding="utf-8")
                input_path = temp_input

            cmd = [
                sys.executable,
                "-m",
                "pipeline.pipeline_runner",
                str(input_path),
            ]
            if self.fail_fast_var.get():
                cmd.append("--fail-fast")
            if self.use_t5_var.get():
                cmd.append("--use-t5")
                cmd.extend(["--t5-mode", self.t5_mode_var.get()])

            self.output_queue.put(("log", "Running: " + " ".join(cmd) + "\n"))
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            self.current_process = process

            assert process.stdout is not None
            for line in process.stdout:
                self.output_queue.put(("log", line))
                if self.cancel_event.is_set():
                    break

            process.wait()
            rc = process.returncode
        except Exception as exc:
            self.output_queue.put(("error", f"Pipeline execution failed: {exc}\n"))
            rc = -1
        finally:
            self.current_process = None

        output_path: Optional[Path] = None
        status_message: Optional[str] = None
        try:
            if rc == 0 and not self.cancel_event.is_set():
                if txt_mode:
                    expected = input_path.with_name(f"{input_path.stem}_corrected.md")
                    if expected.exists():
                        destination = original_path.with_name(f"{original_path.stem}_corrected{original_path.suffix}")
                        shutil.move(str(expected), str(destination))
                        output_path = destination
                else:
                    suffix = original_path.suffix.lower()
                    expected = original_path.with_name(f"{original_path.stem}_corrected{suffix}")
                    if expected.exists():
                        output_path = expected

                if output_path and output_path.exists():
                    status_label = "success"
                    status_message = f"Processing complete. Output saved to {output_path}.\n"
                    self.output_queue.put(("status", status_message))
                else:
                    status_label = "missing_output"
                    status_message = "Processing finished but the output file was not found.\n"
                    self.output_queue.put(("status", status_message))
            elif self.cancel_event.is_set():
                status_label = "cancelled"
                status_message = "Pipeline run cancelled.\n"
                self.output_queue.put(("status", status_message))
            else:
                status_label = "failed"
                status_message = "Pipeline run failed. See logs for details.\n"
                self.output_queue.put(("error", status_message))
        finally:
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

        end_perf = time.perf_counter() if start_perf is not None else None
        actual_seconds: Optional[float] = None
        if start_perf is not None and end_perf is not None:
            actual_seconds = end_perf - start_perf
            estimate_text = f" (estimated ~{estimated_seconds} seconds)" if estimated_seconds else ""
            self.output_queue.put(("log", f"Run duration: {actual_seconds:.1f} seconds{estimate_text}\n"))

        if start_time is not None:
            record = {
                "started_at": start_time,
                "estimated_seconds": estimated_seconds,
                "actual_seconds": actual_seconds,
                "status": status_label,
                "output_path": output_path,
                "status_message": status_message,
            }
            self.run_records.append(record)

        self.output_queue.put(("done", ""))

    # ------------------------------------------------------------------
    # Output handling
    # ------------------------------------------------------------------
    def _poll_output_queue(self) -> None:
        try:
            while True:
                kind, message = self.output_queue.get_nowait()
                if kind == "log":
                    self._append_log(message)
                elif kind == "error":
                    self._append_log(message)
                    self.status_var.set("Error during pipeline run.")
                elif kind == "status":
                    self._append_log(message)
                    self.status_var.set(message.strip())
                elif kind == "done":
                    self.progress.stop()
                    self.run_button.config(state="normal")
                    self.cancel_button.config(state="disabled")
                    self.cancel_event.clear()
        except queue.Empty:
            pass
        finally:
            self.root.after(150, self._poll_output_queue)

    def _append_log(self, message: str) -> None:
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.log_buffer.append(message)

    def _on_close(self) -> None:
        try:
            self._dump_log_file()
        finally:
            self.root.destroy()

    def _dump_log_file(self) -> None:
        if not self.log_buffer and not self.run_records:
            return

        timestamp = datetime.now()
        log_dir = Path.cwd() / "gui_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"pipeline_gui_{timestamp:%Y%m%d_%H%M%S}.log"

        lines: List[str] = []
        lines.append(f"SATCN Pipeline Test Utility log")
        lines.append(f"Session closed at: {timestamp.isoformat()}\n")

        if self.run_records:
            lines.append("Run summary:")
            for idx, record in enumerate(self.run_records, start=1):
                started_at = record.get("started_at")
                est = record.get("estimated_seconds")
                actual = record.get("actual_seconds")
                status = record.get("status")
                output_path = record.get("output_path")
                status_message = record.get("status_message")

                lines.append(f"  Run {idx}:")
                if isinstance(started_at, datetime):
                    lines.append(f"    Started: {started_at.isoformat()}")
                if isinstance(est, int):
                    lines.append(f"    Estimated duration: ~{est} seconds")
                if isinstance(actual, (int, float)):
                    lines.append(f"    Actual duration: {actual:.2f} seconds")
                lines.append(f"    Status: {status}")
                if status_message:
                    lines.append(f"    Status message: {status_message.strip()}")
                if isinstance(output_path, Path):
                    lines.append(f"    Output file: {output_path}")
                lines.append("")

        lines.append("Full pipeline output log:")
        lines.extend(self.log_buffer)

        log_path.write_text("\n".join(lines), encoding="utf-8")

    # ------------------------------------------------------------------
    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    gui = PipelineTestGUI()
    gui.run()


if __name__ == "__main__":
    main()

"""
SATCN LLM GUI - LLM-focused interface for grammar correction.

This GUI focuses on LLM model selection and management:
- Model selection (local GGUF files)
- HuggingFace model downloader
- Model management (browse, download, organize)
- Quantization selection
"""

import json
import math
import queue
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

# Constants
SUPPORTED_FORMATS = {".txt", ".md", ".epub"}
WORDS_PER_PAGE = 300
DEFAULT_WINDOW_SIZE = "1100x700"
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 650

# Default model directory
DEFAULT_MODEL_DIR = Path("models")


class LLMConfig:
    """Configuration for LLM GUI."""

    def __init__(self):
        self.input_file: Path | None = None
        self.model_path: Path | None = None
        self.model_dir: Path = DEFAULT_MODEL_DIR
        self.temperature: float = 0.1
        self.max_tokens: int = 4096
        self.fail_fast: bool = False

    @classmethod
    def get_config_path(cls) -> Path:
        """Get path to config file."""
        return Path.home() / ".satcn" / "llm_gui_config.json"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "input_file": str(self.input_file) if self.input_file else None,
            "model_path": str(self.model_path) if self.model_path else None,
            "model_dir": str(self.model_dir),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "fail_fast": self.fail_fast,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LLMConfig":
        """Create from dictionary."""
        config = cls()
        if data.get("input_file"):
            config.input_file = Path(data["input_file"])
        if data.get("model_path"):
            config.model_path = Path(data["model_path"])
        if data.get("model_dir"):
            config.model_dir = Path(data["model_dir"])
        config.temperature = data.get("temperature", 0.1)
        config.max_tokens = data.get("max_tokens", 4096)
        config.fail_fast = data.get("fail_fast", False)
        return config

    def save(self) -> None:
        """Save configuration."""
        config_path = self.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls) -> "LLMConfig":
        """Load configuration."""
        config_path = cls.get_config_path()
        if config_path.exists():
            try:
                with open(config_path) as f:
                    data = json.load(f)
                return cls.from_dict(data)
            except Exception:
                pass
        return cls()


class SATCNLLMGui:
    """
    LLM-focused GUI for SATCN pipeline.

    Features:
    - Local model selection and management
    - HuggingFace model downloader
    - Model organization
    - Real-time processing feedback
    """

    def __init__(self):
        """Initialize the LLM GUI."""
        # Configuration
        self.config = LLMConfig.load()

        # Ensure model directory exists
        self.config.model_dir.mkdir(parents=True, exist_ok=True)

        # Processing state
        self.processing = False
        self.process_thread: threading.Thread | None = None
        self.cancel_flag = False
        self.output_queue: queue.Queue = queue.Queue()

        # Model management
        self.available_models: list[Path] = []
        self.scan_for_models()

        # File statistics
        self.file_stats: dict | None = None

        # Initialize CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main window
        self.root = ctk.CTk()
        self.root.title("SATCN LLM - Model-Focused Grammar Correction")

        # Window sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        target_height = min(int(screen_height * 0.75), 700)
        target_width = min(1100, int(screen_width * 0.65))

        self.root.geometry(f"{target_width}x{target_height}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Build UI
        self._build_ui()

        # Log GPU status
        self._log_gpu_status()

        # Load previously selected file
        if self.config.input_file and self.config.input_file.exists():
            self._load_file_stats()

        # Keyboard shortcuts
        self._setup_keyboard_shortcuts()

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def scan_for_models(self):
        """Scan for available GGUF models."""
        self.available_models = []

        # Scan model directory
        if self.config.model_dir.exists():
            self.available_models.extend(self.config.model_dir.rglob("*.gguf"))

        # Also check for GRMR-V3 in project root
        project_root = Path.cwd()
        grmr_dir = project_root / ".GRMR-V3-Q4B-GGUF"
        if grmr_dir.exists():
            self.available_models.extend(grmr_dir.glob("*.gguf"))

        # Sort by name
        self.available_models.sort(key=lambda p: p.name)

    def _build_ui(self):
        """Build the complete UI layout."""
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Log section expands

        # TOP: File selection
        self._build_file_section(main_frame, 0)

        # MIDDLE TOP: Model selection
        self._build_model_section(main_frame, 1)

        # MIDDLE BOTTOM: HuggingFace downloader
        self._build_downloader_section(main_frame, 2)

        # BOTTOM: Output log
        self._build_output_section(main_frame, 3)

    def _build_file_section(self, parent, row):
        """Build file selection section."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        frame.columnconfigure(1, weight=1)

        # File selector
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

        # File stats
        stats_label = ctk.CTkLabel(frame, text="📊 Stats:", font=("", 11))
        stats_label.grid(row=1, column=0, sticky="w", padx=10, pady=4)

        self.stats_text = ctk.StringVar(value="No file loaded")
        self.stats_label = ctk.CTkLabel(
            frame, textvariable=self.stats_text, anchor="w", text_color="gray70", font=("", 10)
        )
        self.stats_label.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        # Run controls
        controls_frame = ctk.CTkFrame(frame, fg_color="transparent")
        controls_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(4, 8))
        controls_frame.columnconfigure(1, weight=1)

        self.run_btn = ctk.CTkButton(
            controls_frame,
            text="▶️ Run Correction",
            command=self._run_pipeline,
            fg_color="#2fa572",
            hover_color="#106a43",
            width=140,
            height=32,
        )
        self.run_btn.grid(row=0, column=0, padx=(0, 8))

        self.cancel_btn = ctk.CTkButton(
            controls_frame,
            text="⏹ Cancel",
            command=self._cancel_pipeline,
            fg_color="#d32f2f",
            hover_color="#9a0007",
            width=100,
            state="disabled",
        )
        self.cancel_btn.grid(row=0, column=1, sticky="w")

        self.progress = ctk.CTkProgressBar(controls_frame, mode="indeterminate")
        self.progress.grid(row=0, column=2, sticky="ew", padx=(8, 0))
        self.progress.set(0)

        self.status_var = ctk.StringVar(value="Ready")
        status_label = ctk.CTkLabel(controls_frame, textvariable=self.status_var, font=("", 10))
        status_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

    def _build_model_section(self, parent, row):
        """Build model selection section."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        frame.columnconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(frame, text="🤖 LLM Model Selection", font=("", 13, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 8))

        # Model directory
        dir_label = ctk.CTkLabel(frame, text="Models Folder:", font=("", 11))
        dir_label.grid(row=1, column=0, sticky="w", padx=10, pady=4)

        self.model_dir_var = ctk.StringVar(value=str(self.config.model_dir))
        model_dir_entry = ctk.CTkEntry(frame, textvariable=self.model_dir_var, state="readonly")
        model_dir_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        dir_btn = ctk.CTkButton(frame, text="Change...", command=self._change_model_dir, width=100)
        dir_btn.grid(row=1, column=2, padx=(0, 10), pady=4)

        # Model selection dropdown
        model_label = ctk.CTkLabel(frame, text="Selected Model:", font=("", 11))
        model_label.grid(row=2, column=0, sticky="w", padx=10, pady=4)

        self.model_var = ctk.StringVar(value="")
        model_names = [m.name for m in self.available_models]
        if not model_names:
            model_names = ["No models found"]

        self.model_dropdown = ctk.CTkComboBox(
            frame,
            variable=self.model_var,
            values=model_names,
            command=self._on_model_change,
            state="readonly" if model_names[0] != "No models found" else "disabled",
        )
        self.model_dropdown.grid(row=2, column=1, sticky="ew", padx=8, pady=4)

        # Set default model
        if self.config.model_path and self.config.model_path.exists():
            self.model_var.set(self.config.model_path.name)
        elif model_names and model_names[0] != "No models found":
            self.model_var.set(model_names[0])
            self.config.model_path = self.available_models[0]

        refresh_btn = ctk.CTkButton(
            frame, text="🔄 Refresh", command=self._refresh_models, width=100
        )
        refresh_btn.grid(row=2, column=2, padx=(0, 10), pady=4)

        # Model parameters
        params_frame = ctk.CTkFrame(frame, fg_color="transparent")
        params_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=(4, 10))

        # Temperature
        temp_label = ctk.CTkLabel(params_frame, text="Temperature:", font=("", 10))
        temp_label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.temp_var = ctk.DoubleVar(value=self.config.temperature)
        temp_slider = ctk.CTkSlider(
            params_frame, from_=0.0, to=1.0, variable=self.temp_var, width=150
        )
        temp_slider.grid(row=0, column=1, sticky="ew", padx=8)

        self.temp_value_label = ctk.CTkLabel(
            params_frame, text=f"{self.config.temperature:.2f}", font=("", 10)
        )
        self.temp_value_label.grid(row=0, column=2, padx=(0, 20))
        temp_slider.configure(
            command=lambda v: self.temp_value_label.configure(text=f"{float(v):.2f}")
        )

        # Fail fast checkbox
        self.fail_fast_var = ctk.BooleanVar(value=self.config.fail_fast)
        fail_fast_cb = ctk.CTkCheckBox(
            params_frame, text="Fail fast on errors", variable=self.fail_fast_var
        )
        fail_fast_cb.grid(row=0, column=3, sticky="w", padx=20)

    def _build_downloader_section(self, parent, row):
        """Build HuggingFace downloader section."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        frame.columnconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            frame, text="⬇️ HuggingFace Model Downloader", font=("", 13, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 8))

        # URL input
        url_label = ctk.CTkLabel(frame, text="Model URL:", font=("", 11))
        url_label.grid(row=1, column=0, sticky="w", padx=10, pady=4)

        self.hf_url_var = ctk.StringVar(value="")
        hf_url_entry = ctk.CTkEntry(
            frame, textvariable=self.hf_url_var, placeholder_text="https://huggingface.co/..."
        )
        hf_url_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        download_btn = ctk.CTkButton(
            frame,
            text="Download",
            command=self._download_model,
            fg_color="#1976d2",
            hover_color="#004ba0",
            width=100,
        )
        download_btn.grid(row=1, column=2, padx=(0, 10), pady=4)

        # Download progress
        self.download_status_var = ctk.StringVar(value="Enter a HuggingFace model URL to download")
        download_status = ctk.CTkLabel(
            frame, textvariable=self.download_status_var, font=("", 9), text_color="gray60"
        )
        download_status.grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=(0, 10))

    def _build_output_section(self, parent, row):
        """Build output log section."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        label = ctk.CTkLabel(frame, text="📝 Output Log", font=("", 12, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 6))

        self.output_text = ctk.CTkTextbox(frame, wrap="word", font=("Consolas", 10))
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts."""
        self.root.bind("<Control-o>", lambda e: self._browse_file())
        self.root.bind("<Control-O>", lambda e: self._browse_file())
        self.root.bind(
            "<Control-r>", lambda e: self._run_pipeline() if not self.processing else None
        )
        self.root.bind(
            "<Control-R>", lambda e: self._run_pipeline() if not self.processing else None
        )
        self.root.bind("<Escape>", lambda e: self._cancel_pipeline() if self.processing else None)

    # Event handlers
    def _browse_file(self):
        """Browse for input file."""
        filepath = filedialog.askopenfilename(
            title="Select document to correct",
            filetypes=(
                ("All supported", "*.txt *.md *.epub"),
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("EPUB files", "*.epub"),
                ("All files", "*.*"),
            ),
        )

        if not filepath:
            return

        path = Path(filepath)
        if path.suffix.lower() not in SUPPORTED_FORMATS:
            messagebox.showerror("Unsupported file", f"File type {path.suffix} is not supported.")
            return

        self.config.input_file = path
        self.file_path_var.set(str(path))
        self._load_file_stats()
        self.config.save()

    def _load_file_stats(self):
        """Load file statistics."""
        if not self.config.input_file or not self.config.input_file.exists():
            return

        try:
            # Simple word count for now
            text = self.config.input_file.read_text(encoding="utf-8", errors="ignore")
            words = len(text.split())
            size = self.config.input_file.stat().st_size
            pages = math.ceil(words / WORDS_PER_PAGE) if words else 0

            size_str = self._format_size(size)
            self.stats_text.set(f"{words:,} words | {pages} pages | {size_str}")

        except Exception as e:
            self._log(f"Error loading file stats: {e}")

    def _change_model_dir(self):
        """Change model directory."""
        dirpath = filedialog.askdirectory(
            title="Select model directory", initialdir=self.config.model_dir
        )

        if not dirpath:
            return

        self.config.model_dir = Path(dirpath)
        self.model_dir_var.set(str(self.config.model_dir))
        self.config.save()
        self._refresh_models()

    def _refresh_models(self):
        """Refresh available models list."""
        self.scan_for_models()

        model_names = [m.name for m in self.available_models]
        if not model_names:
            model_names = ["No models found"]

        self.model_dropdown.configure(values=model_names)

        if model_names and model_names[0] != "No models found":
            self.model_var.set(model_names[0])
            self.config.model_path = self.available_models[0]
            self.model_dropdown.configure(state="readonly")
        else:
            self.model_var.set("No models found")
            self.model_dropdown.configure(state="disabled")

        self._log(f"Refreshed models: Found {len(self.available_models)} models")

    def _on_model_change(self, model_name: str):
        """Handle model selection change."""
        for model_path in self.available_models:
            if model_path.name == model_name:
                self.config.model_path = model_path
                self.config.save()
                self._log(f"Selected model: {model_name}")
                break

    def _download_model(self):
        """Download model from HuggingFace."""
        url = self.hf_url_var.get().strip()

        if not url:
            messagebox.showwarning("No URL", "Please enter a HuggingFace model URL")
            return

        if "huggingface.co" not in url:
            messagebox.showerror("Invalid URL", "Please enter a valid HuggingFace URL")
            return

        # Parse HuggingFace URL
        # Format: https://huggingface.co/username/repo-name
        # or: https://huggingface.co/username/repo-name/blob/main/file.gguf
        try:
            parts = url.replace("https://", "").replace("huggingface.co/", "").split("/")

            if len(parts) < 2:
                messagebox.showerror(
                    "Invalid URL", "URL should be: https://huggingface.co/username/repo-name"
                )
                return

            username = parts[0]
            repo_name = parts[1]
            repo_id = f"{username}/{repo_name}"

            # Check if specific file is mentioned
            filename = None
            if len(parts) > 3 and parts[2] in ["blob", "resolve"]:
                # Extract filename from URL
                filename = "/".join(parts[4:])  # Skip 'blob/main/' or 'resolve/main/'

            self._log(f"Downloading from repo: {repo_id}")

            # Start download in background thread
            download_thread = threading.Thread(
                target=self._download_model_thread, args=(repo_id, filename), daemon=True
            )
            download_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse URL: {e}")
            self._log(f"Error parsing URL: {e}")

    def _download_model_thread(self, repo_id: str, filename: str = None):
        """Download model in background thread."""
        try:
            from huggingface_hub import hf_hub_download, list_repo_files

            self.output_queue.put(("log", f"Connecting to HuggingFace: {repo_id}"))
            self.download_status_var.set("Connecting to HuggingFace...")

            # If no specific file, list repo files and find GGUF files
            if not filename:
                self.output_queue.put(("log", "Scanning repository for GGUF files..."))

                try:
                    files = list_repo_files(repo_id)
                    gguf_files = [f for f in files if f.endswith(".gguf")]

                    if not gguf_files:
                        self.output_queue.put(("error", "No GGUF files found in repository"))
                        self.download_status_var.set("Error: No GGUF files found")
                        return

                    if len(gguf_files) == 1:
                        filename = gguf_files[0]
                        self.output_queue.put(("log", f"Found model: {filename}"))
                    else:
                        # Multiple GGUF files - let user choose
                        self.root.after(0, lambda: self._choose_model_file(repo_id, gguf_files))
                        return

                except Exception as e:
                    self.output_queue.put(("error", f"Failed to list repo files: {e}"))
                    self.download_status_var.set("Error listing files")
                    return

            # Download the file
            self.output_queue.put(("log", f"Downloading: {filename}"))
            self.download_status_var.set(f"Downloading {filename}...")

            # Ensure model directory exists
            self.config.model_dir.mkdir(parents=True, exist_ok=True)

            # Download with progress
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=self.config.model_dir,
                local_dir_use_symlinks=False,
                resume_download=True,
            )

            self.output_queue.put(("log", f"✓ Download complete: {local_path}"))
            self.download_status_var.set("✓ Download complete!")

            # Refresh models list
            self.root.after(100, self._refresh_models)

        except Exception as e:
            self.output_queue.put(("error", f"Download failed: {e}"))
            self.download_status_var.set(f"Error: {e}")

    def _choose_model_file(self, repo_id: str, gguf_files: list[str]):
        """Let user choose which GGUF file to download."""
        # Create selection dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Select Model File")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"600x400+{x}+{y}")

        # Title
        title = ctk.CTkLabel(
            dialog, text=f"Multiple GGUF files found in {repo_id}", font=("", 14, "bold")
        )
        title.pack(pady=20)

        # Info
        info = ctk.CTkLabel(dialog, text="Select which model file to download:", font=("", 11))
        info.pack(pady=(0, 10))

        # Listbox frame
        list_frame = ctk.CTkFrame(dialog)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Scrollable frame for radio buttons
        scroll_frame = ctk.CTkScrollableFrame(list_frame)
        scroll_frame.pack(fill="both", expand=True)

        selected_file = ctk.StringVar(value=gguf_files[0])

        # Create radio buttons for each file
        for file in gguf_files:
            rb = ctk.CTkRadioButton(
                scroll_frame, text=f"{file}", variable=selected_file, value=file, font=("", 10)
            )
            rb.pack(anchor="w", pady=2, padx=10)

        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)

        def on_download():
            filename = selected_file.get()
            dialog.destroy()
            # Start download in thread
            download_thread = threading.Thread(
                target=self._download_model_thread, args=(repo_id, filename), daemon=True
            )
            download_thread.start()

        def on_cancel():
            dialog.destroy()
            self.download_status_var.set("Download cancelled")

        download_btn = ctk.CTkButton(
            button_frame,
            text="Download Selected",
            command=on_download,
            fg_color="#2fa572",
            hover_color="#106a43",
            width=150,
        )
        download_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_cancel,
            fg_color="#d32f2f",
            hover_color="#9a0007",
            width=100,
        )
        cancel_btn.pack(side="left", padx=5)

    def _run_pipeline(self):
        """Run the correction pipeline."""
        if self.processing:
            return

        if not self.config.input_file:
            messagebox.showwarning("No file", "Please select an input file first")
            return

        if not self.config.model_path or not self.config.model_path.exists():
            messagebox.showwarning("No model", "Please select a valid model first")
            return

        self.processing = True
        self.cancel_flag = False
        self._set_processing_state(True)

        self._log(f"Starting correction with model: {self.config.model_path.name}")

        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_file, daemon=True)
        self.process_thread.start()

        # Start queue polling
        self.root.after(100, self._check_queue)

    def _cancel_pipeline(self):
        """Cancel the running pipeline."""
        if self.processing:
            self.cancel_flag = True
            self._log("Cancelling...")

    def _process_file(self):
        """Process file in background thread."""
        output_path = None
        stats = {}

        try:
            import time

            from satcn.core.filters.grmr_v3_filter import GRMRV3GrammarFilter

            self.output_queue.put(("log", f"Loading model: {self.config.model_path.name}"))

            # Initialize GRMR-V3 filter with selected model
            # Note: GPU is automatically detected via n_gpu_layers parameter
            filter_instance = GRMRV3GrammarFilter(
                model_path=str(self.config.model_path),
                temperature=self.config.temperature,
                max_new_tokens=self.config.max_tokens,
            )

            self.output_queue.put(("log", f"Model loaded: {self.config.model_path.name}"))
            self.output_queue.put(("log", f"Processing file: {self.config.input_file.name}"))

            # Read input file
            input_text = self.config.input_file.read_text(encoding="utf-8", errors="ignore")

            # Split into paragraphs
            paragraphs = [p.strip() for p in input_text.split("\n\n") if p.strip()]
            total_paragraphs = len(paragraphs)

            self.output_queue.put(("log", f"Found {total_paragraphs} paragraphs to process"))

            # Process each paragraph
            corrected_paragraphs = []
            changes_count = 0
            start_time = time.time()

            for i, paragraph in enumerate(paragraphs, 1):
                if self.cancel_flag:
                    self.output_queue.put(("log", "⚠ Cancelled by user"))
                    self.output_queue.put(("done", "cancelled"))
                    return

                # Update progress
                self.output_queue.put(("log", f"Processing paragraph {i}/{total_paragraphs}..."))

                # Correct the paragraph
                corrected = filter_instance.correct_text(paragraph)
                corrected_paragraphs.append(corrected)

                if corrected != paragraph:
                    changes_count += 1

            elapsed_time = time.time() - start_time

            # Generate output filename
            input_stem = self.config.input_file.stem
            input_suffix = self.config.input_file.suffix
            output_path = self.config.input_file.parent / f"{input_stem}_corrected{input_suffix}"

            # Write output file
            output_text = "\n\n".join(corrected_paragraphs)
            output_path.write_text(output_text, encoding="utf-8")

            # Calculate statistics
            input_words = len(input_text.split())
            output_words = len(output_text.split())
            output_size_kb = output_path.stat().st_size / 1024

            # Stats for SuccessDialog (expects specific format)
            stats = {
                "input_file": str(self.config.input_file),
                "output_file": str(output_path),
                "model": self.config.model_path.name,
                "total_changes": changes_count,  # SuccessDialog expects this key
                "processing_time": elapsed_time,  # Must be float, not string
                "output_size_formatted": f"{output_size_kb:.1f} KB",
                "filters_applied": ["GRMR-V3 Grammar Correction"],
                # Additional info for logging
                "total_paragraphs": total_paragraphs,
                "paragraphs_changed": changes_count,
                "input_words": input_words,
                "output_words": output_words,
                "words_per_second": input_words / elapsed_time if elapsed_time > 0 else 0,
            }

            self.output_queue.put(("log", "✓ Processing complete!"))
            self.output_queue.put(
                ("log", f"  • Changed {changes_count}/{total_paragraphs} paragraphs")
            )
            self.output_queue.put(("log", f"  • Processing time: {elapsed_time:.2f}s"))
            self.output_queue.put(("log", f"  • Speed: {input_words / elapsed_time:.1f} words/sec"))
            self.output_queue.put(("log", f"  • Output saved to: {output_path.name}"))

            # Send success with output path and stats
            self.output_queue.put(("success", (str(output_path), stats)))
            self.output_queue.put(("done", "success"))

        except Exception as e:
            import traceback

            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            self.output_queue.put(("error", error_msg))
            self.output_queue.put(("done", "error"))

    def _check_queue(self):
        """Check output queue for messages."""
        output_path = None
        stats = None

        try:
            while True:
                msg_type, message = self.output_queue.get_nowait()

                if msg_type == "log":
                    self._log(message)
                elif msg_type == "error":
                    self._log(f"ERROR: {message}")
                elif msg_type == "success":
                    # Store output path and stats for success dialog
                    output_path, stats = message
                elif msg_type == "done":
                    self.processing = False
                    self._set_processing_state(False)

                    if message == "success" and output_path:
                        self.status_var.set("✓ Correction complete")
                        # Show success dialog with diff viewer
                        # Use default args to capture current values in closure
                        self.root.after(
                            100, lambda p=output_path, s=stats: self._show_success_dialog(p, s)
                        )
                    elif message == "cancelled":
                        self.status_var.set("⚠ Cancelled")
                    else:
                        self.status_var.set("✗ Error occurred")
                    return

        except queue.Empty:
            pass

        if self.processing:
            self.root.after(100, self._check_queue)

    def _set_processing_state(self, processing: bool):
        """Update UI for processing state."""
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
        self.output_text.see("end")

    def _log_gpu_status(self):
        """Log GPU availability on startup."""
        gpu_info = []

        llama_has_cuda = False
        try:
            from llama_cpp import Llama

            gpu_info.append("✓ llama-cpp-python installed")

            import inspect

            llama_sig = inspect.signature(Llama.__init__)
            if "n_gpu_layers" in llama_sig.parameters:
                gpu_info.append("✓ llama-cpp-python built with GPU support")
                llama_has_cuda = True

            try:
                import torch

                if torch.cuda.is_available():
                    device_name = torch.cuda.get_device_name(0)
                    vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    gpu_info.append(f"✓ CUDA GPU: {device_name} ({vram:.1f} GB VRAM)")
                    gpu_info.append("✓ GPU acceleration available")
                    llama_has_cuda = True
            except ImportError:
                if llama_has_cuda:
                    gpu_info.append("✓ GPU acceleration available (via llama-cpp CUDA)")
                else:
                    gpu_info.append("ℹ PyTorch not available - assuming CPU inference")

        except ImportError:
            gpu_info.append("✗ llama-cpp-python not installed")
            gpu_info.append("✗ LLM inference unavailable")

        self.output_text.insert("end", "=== GPU STATUS ===\n")
        for info in gpu_info:
            self.output_text.insert("end", f"{info}\n")
        self.output_text.insert("end", "==================\n\n")
        self.output_text.see("end")

    def _show_success_dialog(self, output_path: str, stats: dict):
        """Show success dialog with options to view diff or open file."""
        try:
            from satcn.gui.success_dialog import SuccessDialog

            SuccessDialog(
                parent=self.root,
                output_path=Path(output_path),
                stats=stats,
                on_view_diff_callback=lambda: self._open_diff_viewer(
                    Path(stats["input_file"]), Path(output_path)
                ),
                on_open_output_callback=lambda: self._open_output_file(output_path),
            )
        except Exception as e:
            import traceback

            error_msg = f"Error showing success dialog: {e}\n{traceback.format_exc()}"
            self._log(f"ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)

    def _open_diff_viewer(self, original_path: Path, corrected_path: Path):
        """Open diff viewer window."""
        try:
            from satcn.gui.diff_viewer import DiffViewerWindow

            DiffViewerWindow(self.root, original_path=original_path, corrected_path=corrected_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open diff viewer: {e}")
            self._log(f"Error opening diff viewer: {e}")

    def _open_output_file(self, output_path: str):
        """Open output file in default application."""
        try:
            import os
            import platform
            import subprocess

            output_file = Path(output_path)

            if not output_file.exists():
                messagebox.showerror("Error", f"Output file not found: {output_path}")
                return

            # Open file with default application
            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", output_path])
            else:  # Linux
                subprocess.run(["xdg-open", output_path])

            self._log(f"Opened file: {output_file.name}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")
            self._log(f"Error opening file: {e}")

    def _on_closing(self):
        """Handle window closing."""
        if self.processing:
            if not messagebox.askokcancel(
                "Quit", "Processing is running. Are you sure you want to quit?"
            ):
                return
            self.cancel_flag = True

        self.config.save()
        self.root.destroy()

    @staticmethod
    def _format_size(bytes: int) -> str:
        """Format byte size to human readable."""
        if bytes == 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB", "TB"]
        i = min(int(math.log(bytes, 1024)), len(units) - 1)
        return f"{bytes / (1024 ** i):.2f} {units[i]}"

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()


def main():
    """Entry point for LLM GUI."""
    app = SATCNLLMGui()
    app.run()


if __name__ == "__main__":
    main()

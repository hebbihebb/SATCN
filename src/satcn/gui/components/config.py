"""
Configuration state management for SATCN Pipeline GUI.

This module defines the PipelineConfig dataclass which mirrors CLI arguments
and serves as a single source of truth for pipeline execution settings.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

# Grammar engine options
GrammarEngine = Literal["languagetool", "grmr-v3", "t5", "none"]
CorrectionMode = Literal["replace", "hybrid", "supplement"]


@dataclass
class PipelineConfig:
    """
    Pipeline configuration matching CLI arguments.

    This dataclass can be serialized to JSON for config persistence
    and directly maps to PipelineRunner constructor arguments.
    """

    # Input/output
    input_file: Path | None = None
    output_file: Path | None = None  # Auto-generated if None

    # Grammar correction strategy (mutually exclusive)
    grammar_engine: GrammarEngine = "grmr-v3"  # Default to best option

    # Correction modes (only used when engine is grmr-v3 or t5)
    grmr_mode: CorrectionMode = "replace"
    t5_mode: CorrectionMode = "replace"

    # Pipeline options
    fail_fast: bool = False

    # Advanced options (future implementation)
    gpu_enabled: bool = True
    temperature: float = 0.1  # GRMR-V3 parameter
    max_tokens: int = 4096
    log_level: str = "INFO"

    @property
    def use_grmr(self) -> bool:
        """Check if GRMR-V3 engine is selected."""
        return self.grammar_engine == "grmr-v3"

    @property
    def use_t5(self) -> bool:
        """Check if T5 engine is selected."""
        return self.grammar_engine == "t5"

    @property
    def active_mode(self) -> CorrectionMode:
        """Return the mode for the currently selected grammar engine."""
        if self.use_grmr:
            return self.grmr_mode
        elif self.use_t5:
            return self.t5_mode
        return "replace"

    def to_dict(self) -> dict:
        """
        Convert config to dictionary for JSON serialization.

        Converts Path objects to strings for JSON compatibility.
        """
        data = asdict(self)
        # Convert Path objects to strings
        if data.get("input_file"):
            data["input_file"] = str(data["input_file"])
        if data.get("output_file"):
            data["output_file"] = str(data["output_file"])
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineConfig":
        """
        Create config from dictionary (JSON deserialization).

        Converts string paths back to Path objects.
        """
        # Convert string paths to Path objects
        if data.get("input_file"):
            data["input_file"] = Path(data["input_file"])
        if data.get("output_file"):
            data["output_file"] = Path(data["output_file"])
        return cls(**data)

    def save(self, path: Path) -> None:
        """
        Save configuration to JSON file.

        Creates parent directories if they don't exist.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "PipelineConfig":
        """
        Load configuration from JSON file.

        Returns default config if file doesn't exist.
        """
        if not path.exists():
            return cls()  # Return defaults

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def get_config_path(cls) -> Path:
        """
        Get the standard config file location.

        Uses XDG Base Directory spec: ~/.config/satcn/gui_config.json
        Falls back to user home on Windows if .config doesn't exist.
        """
        home = Path.home()
        config_dir = home / ".config" / "satcn"

        # Windows fallback: use AppData if .config doesn't feel natural
        # But we'll try .config first for consistency
        return config_dir / "gui_config.json"

    def validate(self) -> list[str]:
        """
        Validate configuration and return list of error messages.

        Returns empty list if valid.
        """
        errors = []

        if not self.input_file:
            errors.append("No input file selected")
        elif not self.input_file.exists():
            errors.append(f"Input file not found: {self.input_file}")
        elif self.input_file.suffix not in {".txt", ".md", ".epub"}:
            errors.append(
                f"Unsupported file format: {self.input_file.suffix}. "
                f"Expected .txt, .md, or .epub"
            )

        return errors

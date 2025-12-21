# pipeline/filters/grmr_v3_filter.py

"""
GRMR-V3 GGUF Grammar Filter

This filter uses a quantized GGUF model via llama.cpp for grammar and spelling
correction. It provides a local, offline alternative to T5 models with potentially
better quality and the ability to handle longer context windows.

Model: GRMR-V3-Q4B.Q4_K_M.gguf (4-bit quantized)
Runtime: llama-cpp-python bindings
Context window: 4096 tokens (vs T5's 512)
"""

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

try:
    from llama_cpp import Llama

    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    Llama = None


def find_model_path(
    explicit_path: str | Path | None = None,
    model_filename: str = "GRMR-V3-Q4B.Q4_K_M.gguf",
) -> Path | None:
    """
    Search for the GGUF model file in multiple locations.

    Search order:
    1. Explicit path (if provided)
    2. Environment variable: SATCN_GRMR_MODEL_PATH
    3. Config file: ~/.satcn/llm_gui_config.json (model_path field)
    4. Virtual environment: {venv}/.GRMR-V3-Q4B-GGUF/
    5. Current working directory: .GRMR-V3-Q4B-GGUF/
    6. User config directory: ~/.satcn/models/
    7. Package installation directory

    Args:
        explicit_path: Explicitly provided model path
        model_filename: Name of the model file to search for

    Returns:
        Path to the model file if found, None otherwise
    """
    search_paths = []

    # 1. Explicit path
    if explicit_path:
        explicit = Path(explicit_path)
        if explicit.is_file():
            return explicit
        # If explicit path is a directory, look for the model file inside
        if explicit.is_dir():
            search_paths.append(explicit / model_filename)

    # 2. Environment variable
    env_path = os.environ.get("SATCN_GRMR_MODEL_PATH")
    if env_path:
        env_path_obj = Path(env_path)
        if env_path_obj.is_file():
            return env_path_obj
        if env_path_obj.is_dir():
            search_paths.append(env_path_obj / model_filename)

    # 3. Config file
    config_path = Path.home() / ".satcn" / "llm_gui_config.json"
    if config_path.exists():
        try:
            import json

            with open(config_path) as f:
                config = json.load(f)
                if config.get("model_path"):
                    config_model_path = Path(config["model_path"])
                    if config_model_path.exists():
                        search_paths.append(config_model_path)
        except Exception:
            pass  # Ignore config parsing errors

    # 4. Virtual environment directory
    # Check if we're in a virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        # We're in a venv
        venv_path = Path(sys.prefix)
        search_paths.append(venv_path / ".GRMR-V3-Q4B-GGUF" / model_filename)

    # 5. Current working directory
    search_paths.append(Path.cwd() / ".GRMR-V3-Q4B-GGUF" / model_filename)

    # 6. User config directory
    search_paths.append(Path.home() / ".satcn" / "models" / model_filename)

    # 7. Package installation directory
    try:
        # Get the directory where this module is installed
        package_dir = Path(__file__).parent.parent.parent.parent
        search_paths.append(package_dir / ".GRMR-V3-Q4B-GGUF" / model_filename)
    except Exception:
        pass

    # Search all paths
    for path in search_paths:
        if path.exists() and path.is_file():
            return path

    return None


class GRMRV3GrammarFilter:
    """
    A filter that uses a local GGUF model for grammar and spelling correction.

    This filter wraps the llama.cpp runtime to perform deterministic,
    context-aware grammar corrections using a quantized model file.

    The model path is automatically searched in multiple locations:
    1. Explicit path (if provided via model_path parameter)
    2. Environment variable: SATCN_GRMR_MODEL_PATH
    3. Config file: ~/.satcn/llm_gui_config.json
    4. Virtual environment directory
    5. Current working directory
    6. User config directory (~/.satcn/models/)
    7. Package installation directory
    """

    # Prompt template for grammar correction
    PROMPT_TEMPLATE = """### Instruction
You are a copy editor. Fix grammar, spelling, and punctuation while keeping character names, slang, and factual content unchanged. Respond with the corrected text only.

### Input
{text}

### Response
"""

    def __init__(
        self,
        model_path: str | None = None,
        n_ctx: int = 4096,
        max_new_tokens: int = 256,
        temperature: float = 0.1,
        top_p: float = 0.15,
        top_k: int = 40,
        min_p: float = 0.01,
        repeat_penalty: float = 1.05,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        device: str | None = None,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize the GRMR-V3 grammar correction filter.

        NOTE: Default parameters are from the official GRMR-V3-G4B model card.
        For more deterministic/conservative corrections, use temperature=0.1.

        Args:
            model_path: Path to the .gguf model file. If not provided, searches multiple locations automatically.
            n_ctx: Context window size (default: 4096 tokens)
            max_new_tokens: Maximum tokens to generate per correction (default: 256)
            temperature: Sampling temperature - 0.1 for deterministic (default: 0.1)
            top_p: Nucleus sampling parameter (default: 0.15)
            top_k: Top-k sampling parameter (default: 40)
            min_p: Minimum probability threshold (default: 0.01)
            repeat_penalty: Penalty for repeating tokens (default: 1.05)
            frequency_penalty: Frequency penalty (default: 0.0)
            presence_penalty: Presence penalty (default: 0.0)
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
            logger: Logger instance (creates one if not provided)
        """
        self.logger = logger or logging.getLogger(__name__)

        # Check if llama-cpp-python is available
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError(
                "llama-cpp-python is not installed. "
                "Install it with: pip install -r requirements-grmr.txt\n"
                "For GPU support, see installation instructions in requirements-grmr.txt"
            )

        # Resolve model path using smart search
        resolved_path = find_model_path(explicit_path=model_path)

        if resolved_path is None:
            # Provide helpful error message with search locations
            search_locations = [
                "1. Explicit path via --grmr-model-path CLI argument",
                "2. Environment variable: SATCN_GRMR_MODEL_PATH",
                "3. Config file: ~/.satcn/llm_gui_config.json",
                "4. Virtual environment: {venv}/.GRMR-V3-Q4B-GGUF/",
                "5. Current directory: .GRMR-V3-Q4B-GGUF/",
                "6. User config: ~/.satcn/models/",
                "7. Package install directory",
            ]
            error_msg = (
                f"GGUF model file not found.\n\n"
                f"Searched the following locations:\n" + "\n".join(search_locations) + "\n\n"
                f"Solutions:\n"
                f"  • Download the model and place it in one of the locations above\n"
                f"  • Use --grmr-model-path to specify a custom location\n"
                f"  • Set environment variable: export SATCN_GRMR_MODEL_PATH=/path/to/model.gguf\n"
                f"  • Configure via GUI: Model path will be saved to ~/.satcn/llm_gui_config.json"
            )
            if model_path:
                error_msg = f"Model not found at specified path: {model_path}\n\n" + error_msg
            raise FileNotFoundError(error_msg)

        self.model_path = resolved_path
        self.logger.info(f"Using model at: {self.model_path}")

        # Store generation parameters (following GRMR-V3-G4B model card recommendations)
        self.n_ctx = n_ctx
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.min_p = min_p
        self.repeat_penalty = repeat_penalty
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

        # Determine GPU layers based on device
        if device is None:
            # Auto-detect: Check if llama-cpp-python was built with CUDA support
            use_gpu = False

            # First, check if llama-cpp-python has GPU support by inspecting parameters
            import inspect

            llama_sig = inspect.signature(Llama.__init__)
            has_gpu_param = "n_gpu_layers" in llama_sig.parameters

            if has_gpu_param:
                self.logger.info(
                    "llama-cpp-python has n_gpu_layers parameter - CUDA build detected"
                )

                # Check if CUDA is actually available
                try:
                    import torch

                    if torch.cuda.is_available():
                        use_gpu = True
                        self.logger.info(f"PyTorch CUDA available: {torch.cuda.get_device_name(0)}")
                    else:
                        self.logger.warning("PyTorch CUDA not available - falling back to CPU")
                except ImportError:
                    # PyTorch not installed, but llama-cpp-python may still have CUDA
                    # Try to use GPU anyway - llama-cpp will report if it fails
                    use_gpu = True
                    self.logger.info(
                        "PyTorch not installed - attempting GPU via llama-cpp-python CUDA"
                    )
            else:
                self.logger.warning(
                    "llama-cpp-python built without GPU support (missing n_gpu_layers parameter)"
                )
                self.logger.warning(
                    'Install CUDA-enabled build: pip install llama-cpp-python --force-reinstall --no-cache-dir --config-settings cmake.args="-DGGML_CUDA=ON"'
                )

            device = "cuda" if use_gpu else "cpu"

        self.device = device
        n_gpu_layers = -1 if device == "cuda" else 0

        if device == "cuda":
            self.logger.info(
                f"Initializing GRMR-V3 with GPU acceleration (n_gpu_layers={n_gpu_layers})"
            )
        else:
            self.logger.warning(
                "Initializing GRMR-V3 with CPU inference (will be slower). "
                "For GPU acceleration, reinstall llama-cpp-python with CUDA support."
            )

        # Initialize the model
        try:
            self.logger.info(f"Loading GRMR-V3 GGUF model from {self.model_path}")
            start_time = time.time()

            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                use_mlock=True,  # Lock model in RAM for better performance
                use_mmap=True,  # Memory-map the model file
                verbose=True,  # Enable verbose to see GPU usage logs
            )

            load_time = time.time() - start_time
            self.logger.info(f"GRMR-V3 model loaded successfully in {load_time:.2f}s")

            # Verify GPU usage
            if device == "cuda":
                self.logger.info(
                    "⚠️  IMPORTANT: Check console output above for 'CUDA' or 'GPU' messages"
                )
                self.logger.info(
                    "⚠️  If you see 'llama_model_load' without GPU mentions, llama-cpp-python is using CPU"
                )
                self.logger.info(
                    "⚠️  GPU usage should show 'ggml_cuda_init' or similar CUDA initialization messages"
                )

        except Exception as e:
            self.logger.error(f"Failed to load GRMR-V3 model: {e}")
            raise

        # Statistics tracking
        self.stats = {
            "corrections_made": 0,
            "total_blocks_processed": 0,
            "total_tokens_generated": 0,
            "total_duration_ms": 0,
        }

    def _build_prompt(self, text: str) -> str:
        """
        Build the prompt for grammar correction.

        Args:
            text: Input text to correct

        Returns:
            Formatted prompt string
        """
        return self.PROMPT_TEMPLATE.format(text=text)

    def correct_text(self, text: str) -> str:
        """
        Correct a single text string using the GRMR-V3 model.

        Args:
            text: Input text to correct

        Returns:
            Corrected text
        """
        if not text or len(text.strip()) == 0:
            return text

        try:
            # Build prompt
            prompt = self._build_prompt(text)

            # Check context length
            # Rough estimate: 1 token ≈ 4 characters
            estimated_tokens = len(prompt) // 4
            if estimated_tokens > self.n_ctx - self.max_new_tokens:
                self.logger.warning(
                    f"Text may exceed context window ({estimated_tokens} est. tokens). "
                    f"Consider splitting into smaller chunks."
                )

            # Generate correction with deterministic parameters
            start_time = time.time()

            response = self.llm(
                prompt,
                max_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                min_p=self.min_p,
                repeat_penalty=self.repeat_penalty,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                stop=["###", "\n\n\n"],  # Stop at section markers or excessive newlines
                echo=False,  # Don't echo the prompt
            )

            duration_ms = (time.time() - start_time) * 1000

            # Extract corrected text
            corrected = response["choices"][0]["text"].strip()

            # Update statistics
            tokens_generated = response["usage"]["completion_tokens"]
            self.stats["total_tokens_generated"] += tokens_generated
            self.stats["total_duration_ms"] += duration_ms

            # Log performance
            self.logger.debug(
                f"Corrected {len(text)} chars -> {len(corrected)} chars "
                f"({tokens_generated} tokens, {duration_ms:.0f}ms)"
            )

            return corrected

        except Exception as e:
            self.logger.error(f"Error correcting text with GRMR-V3: {e}")
            # Return original text on error
            return text

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Process pipeline data, correcting grammar in each text block.

        Args:
            data: Pipeline data containing 'text_blocks'

        Returns:
            Modified data with corrected text blocks
        """
        if "text_blocks" not in data:
            self.logger.warning("No text_blocks found in data")
            return data

        corrections_made = 0
        blocks_processed = 0

        for i, block in enumerate(data["text_blocks"]):
            original_content = block.get("content", "")

            if not original_content or len(original_content.strip()) == 0:
                continue

            blocks_processed += 1

            # Correct the text
            corrected_content = self.correct_text(original_content)

            # Update block if changed
            if corrected_content != original_content:
                block["content"] = corrected_content
                corrections_made += 1

                # Calculate word-level changes
                original_words = len(original_content.split())
                corrected_words = len(corrected_content.split())
                word_diff = corrected_words - original_words

                self.logger.debug(
                    f"Block {i}: {original_words} words -> {corrected_words} words "
                    f"({word_diff:+d} word change)"
                )

        # Update global statistics
        self.stats["corrections_made"] += corrections_made
        self.stats["total_blocks_processed"] += blocks_processed

        # Log summary
        avg_duration = (
            self.stats["total_duration_ms"] / blocks_processed if blocks_processed > 0 else 0
        )

        self.logger.info(
            f"GRMR-V3 filter processed {blocks_processed} blocks, "
            f"corrected {corrections_made} ({avg_duration:.0f}ms avg per block)"
        )

        return data

    def get_stats(self) -> dict[str, Any]:
        """
        Get processing statistics.

        Returns:
            Dictionary containing correction statistics
        """
        return self.stats.copy()

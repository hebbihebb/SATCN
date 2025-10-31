"""
T5-based Text Correction Module

This module provides a T5 transformer-based approach to grammar and spelling
correction. It wraps Hugging Face transformers models to provide context-aware
text corrections that go beyond simple rule-based or dictionary approaches.

Experimental Phase:
    This is an experimental integration focused on getting T5 running cleanly
    within the SATCN pipeline. Future iterations will address:
    - Edit constraints and guardrails
    - Slang/informal language masking
    - Domain-specific fine-tuning
    - Over-correction mitigation

Example:
    # Standalone usage
    corrector = T5Corrector()
    corrected = corrector.correct("This sentance have many erors.")

    # Batch correction
    texts = ["Text one with erors", "Text two with misteaks"]
    corrected_texts = corrector.correct_batch(texts)

    # Pipeline integration
    corrector = T5Corrector()
    data = corrector.process(pipeline_data)
"""

import logging

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class T5Corrector:
    """
    A T5-based text correction engine for grammar and spelling.

    This class wraps a T5 sequence-to-sequence model fine-tuned for grammar
    and spelling correction. It provides both standalone correction methods
    and pipeline integration support.

    Attributes:
        model_name (str): Hugging Face model identifier or local path
        device (str): Computing device ('cuda', 'cpu', 'mps')
        max_length (int): Maximum sequence length for tokenization
        tokenizer: Hugging Face tokenizer instance
        model: Hugging Face model instance
    """

    # Default model: FLAN-T5 large for grammar synthesis
    # Grade: C/C+ - changes names but good grammar fixes
    DEFAULT_MODEL = "pszemraj/flan-t5-large-grammar-synthesis"

    # Alternative models (tested and not recommended)
    ALTERNATIVE_MODELS = {
        "ai-forever-spell": "ai-forever/T5-large-spell",  # Grade D+: introduces more errors than fixes
        "small-typo": "willwade/t5-small-spoken-typo",  # Untested - truncates too aggressively
        "general-correction": "rihebriri/t5-text-correction",  # Untested
    }

    # Model-specific prefixes (some models require task prefixes)
    MODEL_PREFIXES = {
        "ai-forever/T5-large-spell": "grammar: ",  # Required but model still performs poorly
        "rihebriri/t5-text-correction": "",  # May need testing
        # Most other models don't need prefixes
    }

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        max_length: int = 512,
        num_beams: int = 2,  # Reduced from 4 for faster, less creative corrections
        use_half_precision: bool = True,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize the T5 corrector.

        Args:
            model_name: Hugging Face model ID or local path. If None, uses
                       DEFAULT_MODEL (flan-t5-large-grammar-synthesis)
            device: Computing device ('cuda', 'cpu', 'mps', or None for auto)
            max_length: Maximum sequence length for input/output (default: 512)
            num_beams: Number of beams for beam search (default: 2, higher =
                      better quality but slower. Reduced from 4 for faster,
                      less creative corrections)
            use_half_precision: Use float16 on GPU for faster inference with
                              minimal quality loss (default: True)
            logger: Optional logger instance. If None, creates a new logger.

        Raises:
            RuntimeError: If model fails to load
            ValueError: If invalid parameters are provided
        """
        self.logger = logger or logging.getLogger(__name__)
        self.model_name = model_name or self.DEFAULT_MODEL
        self.max_length = max_length
        self.num_beams = num_beams
        self.use_half_precision = use_half_precision

        # Get model-specific prefix if required
        self.prefix = self.MODEL_PREFIXES.get(self.model_name, "")
        if self.prefix:
            self.logger.info(f"Model requires prefix: '{self.prefix}'")

        # Auto-detect device if not specified
        self.device = self._detect_device(device)

        # Load model and tokenizer
        self._load_model()

        # Statistics tracking
        self.stats = {"corrections_made": 0, "texts_processed": 0, "errors": 0}

    def _detect_device(self, device: str | None) -> str:
        """
        Detect the best available computing device.

        Args:
            device: User-specified device or None for auto-detection

        Returns:
            str: Device to use ('cuda', 'mps', or 'cpu')
        """
        if device is not None:
            return device

        # Check for NVIDIA CUDA
        if torch.cuda.is_available():
            self.logger.info(f"CUDA detected: {torch.cuda.get_device_name(0)}")
            return "cuda"

        # Check for Apple Silicon MPS
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self.logger.info("Apple Silicon MPS detected")
            return "mps"

        # Fallback to CPU
        self.logger.warning(
            "No GPU detected. Using CPU. "
            "This will be significantly slower (~10-50x). "
            "Consider using a GPU for better performance."
        )
        return "cpu"

    def _load_model(self):
        """
        Load the T5 model and tokenizer.

        Raises:
            RuntimeError: If model loading fails
        """
        try:
            self.logger.info(f"Loading T5 model: {self.model_name}")
            self.logger.info(f"Device: {self.device}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, model_max_length=self.max_length
            )

            # Determine dtype based on device and half precision setting
            if self.device in ["cuda", "mps"] and self.use_half_precision:
                dtype = torch.float16
                self.logger.info("Using half precision (float16)")
            else:
                dtype = torch.float32
                self.logger.info("Using full precision (float32)")

            # Load model with modern API (dtype not torch_dtype, device_map for auto placement)
            load_kwargs = {
                "dtype": dtype,  # Modern API: dtype instead of torch_dtype
            }

            # Load model directly - device_map="auto" is too slow for single GPU
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name, **load_kwargs)

            # Move model to device
            self.model = self.model.to(self.device)

            # Set to evaluation mode
            self.model.eval()

            self.logger.info("T5 model loaded successfully")

            # Log model size
            param_count = sum(p.numel() for p in self.model.parameters())
            self.logger.info(f"Model parameters: {param_count:,}")

        except Exception as e:
            self.logger.error(f"Failed to load T5 model: {e}", exc_info=True)
            raise RuntimeError(f"Could not load T5 model '{self.model_name}': {e}") from e

    def correct(self, text: str, return_confidence: bool = False) -> str | tuple[str, float]:
        """
        Correct a single text string.

        This is the primary method for standalone text correction. It handles
        empty strings, applies the model, and returns the corrected text.

        Args:
            text: Input text to correct
            return_confidence: If True, returns (corrected_text, confidence_score)
                             where confidence is a placeholder for future enhancement

        Returns:
            If return_confidence is False: corrected text string
            If return_confidence is True: tuple of (corrected_text, confidence_score)

        Example:
            >>> corrector = T5Corrector()
            >>> corrector.correct("Thiss sentance have erors.")
            "This sentence has errors."
        """
        # Handle edge cases
        if not text or not text.strip():
            result = text
            if return_confidence:
                return result, 1.0  # Perfect confidence for empty string
            return result

        try:
            # Add model-specific prefix if required
            input_text = self.prefix + text if self.prefix else text

            # Tokenize
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                max_length=self.max_length,
                truncation=True,
                padding=False,
            )

            # Check for truncation
            input_length = inputs["input_ids"].shape[1]
            if input_length >= self.max_length:
                self.logger.warning(
                    f"Text was truncated to {self.max_length} tokens. "
                    f"Original text: {len(text)} chars, {len(text.split())} words. "
                    f"Consider using shorter text blocks or increasing max_length."
                )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate correction
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_length,
                    num_beams=self.num_beams,
                    early_stopping=True,
                    do_sample=False,  # Deterministic output (no sampling randomness)
                    length_penalty=1.0,  # Neutral length penalty (maintain original length)
                    repetition_penalty=1.2,  # Penalize repetitions to prevent duplications
                    no_repeat_ngram_size=3,  # Prevent 3-gram repetitions
                )

            # Decode
            corrected = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Update statistics
            self.stats["texts_processed"] += 1
            if corrected != text:
                self.stats["corrections_made"] += 1

            # Note: Confidence scoring is a future enhancement
            # Currently returns a placeholder
            confidence = 1.0

            if return_confidence:
                return corrected, confidence
            return corrected

        except Exception as e:
            self.logger.error(f"Error correcting text: {e}", exc_info=True)
            self.stats["errors"] += 1

            # Return original text on error (fail gracefully)
            if return_confidence:
                return text, 0.0
            return text

    def correct_batch(self, texts: list[str], show_progress: bool = False) -> list[str]:
        """
        Correct multiple texts.

        Note: This currently processes texts sequentially. Future optimization
        will add true batch processing for better GPU utilization.

        Args:
            texts: List of text strings to correct
            show_progress: If True, logs progress (useful for large batches)

        Returns:
            List of corrected text strings

        Example:
            >>> texts = ["Sentance one.", "Sentance too."]
            >>> corrector.correct_batch(texts)
            ["Sentence one.", "Sentence two."]
        """
        corrected_texts = []

        for i, text in enumerate(texts):
            if show_progress and (i + 1) % 10 == 0:
                self.logger.info(f"Processing {i + 1}/{len(texts)}...")

            corrected = self.correct(text)
            corrected_texts.append(corrected)

        return corrected_texts

    def process(self, data: dict) -> dict:
        """
        Process pipeline data (for integration with SATCN pipeline).

        This method follows the SATCN pipeline filter interface. It expects
        a dictionary with 'text_blocks' and processes each block's content.

        Args:
            data: Pipeline data dictionary containing:
                - text_blocks: List of dicts with 'content' and 'metadata'
                - Other pipeline-specific keys

        Returns:
            Modified data dictionary with corrected text blocks

        Example:
            >>> data = {
            ...     'text_blocks': [
            ...         {'content': 'Sentance with eror', 'metadata': {...}},
            ...     ],
            ...     'format': 'markdown'
            ... }
            >>> corrector.process(data)
        """
        if "text_blocks" not in data:
            self.logger.warning("No 'text_blocks' found in pipeline data")
            return data

        corrections_made = 0
        blocks_processed = 0
        total_blocks = len(data["text_blocks"])

        self.logger.info(f"Processing {total_blocks} text blocks with T5 model...")

        for i, block in enumerate(data["text_blocks"]):
            original_content = block.get("content", "")

            # Skip empty blocks
            if not original_content or not original_content.strip():
                continue

            # Log progress for each block
            word_count = len(original_content.split())
            self.logger.info(
                f"Processing block {i+1}/{total_blocks} "
                f"({word_count} words, {len(original_content)} chars)..."
            )

            # Correct the text
            corrected_content = self.correct(original_content)

            # Update block if changed
            if corrected_content != original_content:
                block["content"] = corrected_content
                corrections_made += 1

                # Calculate change metrics
                orig_words = len(original_content.split())
                corr_words = len(corrected_content.split())
                word_diff = corr_words - orig_words

                self.logger.info(
                    f"Block {i+1}: Corrected "
                    f"(word count: {orig_words} -> {corr_words}, diff: {word_diff:+d})"
                )

                # Log changes (truncated for readability)
                if self.logger.isEnabledFor(logging.DEBUG):
                    orig_preview = original_content[:80].replace("\n", " ")
                    corr_preview = corrected_content[:80].replace("\n", " ")
                    self.logger.debug(f"Block {i+1} BEFORE: '{orig_preview}...'")
                    self.logger.debug(f"Block {i+1} AFTER:  '{corr_preview}...'")
            else:
                self.logger.info(f"Block {i+1}: No changes needed")

            blocks_processed += 1

        self.logger.info(
            f"T5 correction complete: {corrections_made} blocks modified "
            f"out of {blocks_processed} processed"
        )

        return data

    def get_stats(self) -> dict[str, int]:
        """
        Get correction statistics.

        Returns:
            Dictionary with keys:
            - corrections_made: Number of texts that were modified
            - texts_processed: Total number of texts processed
            - errors: Number of errors encountered
        """
        return self.stats.copy()

    def reset_stats(self):
        """Reset correction statistics to zero."""
        self.stats = {"corrections_made": 0, "texts_processed": 0, "errors": 0}

    @classmethod
    def list_models(cls) -> dict[str, str]:
        """
        List available alternative T5 models.

        Returns:
            Dictionary mapping model nicknames to Hugging Face model IDs
        """
        return {"default": cls.DEFAULT_MODEL, **cls.ALTERNATIVE_MODELS}

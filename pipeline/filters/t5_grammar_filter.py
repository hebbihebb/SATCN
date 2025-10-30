# pipeline/filters/t5_grammar_filter.py

import logging
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class T5GrammarFilter:
    """
    A filter that uses a T5 model for grammar and spelling correction.

    This filter uses a fine-tuned FLAN-T5 model to perform context-aware
    grammar and spelling corrections. It can handle complex sentence-level
    issues that rule-based systems may miss.

    Model: pszemraj/flan-t5-large-grammar-synthesis
    """

    def __init__(self, model_name="pszemraj/flan-t5-large-grammar-synthesis",
                 max_length=512, device=None):
        """
        Initialize the T5 grammar correction filter.

        Args:
            model_name (str): Hugging Face model identifier or local path
            max_length (int): Maximum sequence length for tokenization
            device (str): Device to use ('cuda', 'cpu', or None for auto)
        """
        self.logger = logging.getLogger(__name__)
        self.max_length = max_length

        # Determine device
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
                self.logger.info("Using CUDA for T5 inference")
            else:
                device = "cpu"
                self.logger.warning("CUDA not available, using CPU (this will be slow)")

        self.device = device

        try:
            self.logger.info(f"Loading T5 model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

            # Use float16 for GPU, float32 for CPU
            dtype = torch.float16 if device == "cuda" else torch.float32

            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                torch_dtype=dtype,
                device_map=device if device == "cuda" else None
            )

            if device == "cpu":
                self.model = self.model.to(device)

            self.model.eval()  # Set to evaluation mode
            self.logger.info("T5 model loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load T5 model: {e}")
            raise

    def correct_text(self, text):
        """
        Correct a single text string using the T5 model.

        Args:
            text (str): Input text to correct

        Returns:
            str: Corrected text
        """
        if not text or len(text.strip()) == 0:
            return text

        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=self.max_length,
                truncation=True,
                padding=False
            )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate correction
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_length,
                    num_beams=4,  # Beam search for better quality
                    early_stopping=True
                )

            # Decode output
            corrected = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            return corrected

        except Exception as e:
            self.logger.error(f"Error correcting text: {e}")
            # Return original text on error
            return text

    def process(self, data):
        """
        Process the data, correcting grammar and spelling in each text block.

        Args:
            data (dict): Pipeline data containing 'text_blocks'

        Returns:
            dict: Modified data with corrected text blocks
        """
        if 'text_blocks' not in data:
            self.logger.warning("No text_blocks found in data")
            return data

        corrections_made = 0

        for i, block in enumerate(data['text_blocks']):
            original_content = block.get('content', '')

            if not original_content or len(original_content.strip()) == 0:
                continue

            # Correct the text
            corrected_content = self.correct_text(original_content)

            # Update block if changed
            if corrected_content != original_content:
                block['content'] = corrected_content
                corrections_made += 1
                self.logger.debug(f"Block {i}: '{original_content[:50]}...' -> '{corrected_content[:50]}...'")

        self.logger.info(f"T5 grammar filter corrected {corrections_made} blocks")

        return data

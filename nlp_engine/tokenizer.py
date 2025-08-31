# !/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: nlp_engine/tokenizer.py :: Module Integrity Directive
# Self-improving tokenizer for GremlinGPT.
# This script is a component of the GremlinGPT system, under Alpha expansion.

# Refactored to use centralized imports from NLP environment
from environments.nlp import (
    re, transformers, CFG, logger, datetime, nltk
)

# Import custom functions separately to avoid circular imports
try:
    from memory.vector_store.embedder import embed_text, package_embedding, inject_watermark
except ImportError:
    embed_text = package_embedding = inject_watermark = None

# Local project imports that can't be centralized
try:
    from utils.nltk_setup import setup_nltk_data
    NLTK_DATA_DIR = setup_nltk_data()
except ImportError:
    NLTK_DATA_DIR = None

# Try to get AutoTokenizer from transformers if available
try:
    if transformers:
        from transformers import AutoTokenizer
    else:
        AutoTokenizer = None
except ImportError:
    AutoTokenizer = None

WATERMARK = "source:GremlinGPT"
ORIGIN = "tokenizer"
MODEL = CFG["nlp"].get("tokenizer_model", "bert-base-uncased")


try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    logger.success(f"[TOKENIZER] Loaded: {MODEL}")
except Exception as e:
    logger.warning(f"[TOKENIZER] Failed to load {MODEL}. Falling back to nltk: {e}")
    tokenizer = None


def clean_text(text):
    """
    Normalizes whitespace and removes non-ASCII characters.
    """
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", "", text)
    return text.strip()


def tokenize(text, max_length=512, add_special_tokens=True):
    """
    Tokenize text using the loaded model or fallback to NLTK
    """
    if not text or not isinstance(text, str):
        return []
    
    text = clean_text(text)
    
    if tokenizer:
        try:
            # Use HuggingFace tokenizer
            result = tokenizer.encode(
                text, 
                max_length=max_length, 
                truncation=True,
                add_special_tokens=add_special_tokens
            )
            return result
        except Exception as e:
            logger.warning(f"[TOKENIZER] HF tokenization failed: {e}")
    
    # Fallback to NLTK
    if nltk:
        try:
            from nltk.tokenize import word_tokenize
            return word_tokenize(text)
        except Exception as e:
            logger.warning(f"[TOKENIZER] NLTK tokenization failed: {e}")
    
    # Ultimate fallback: simple split
    return text.split()


class Tokenizer:
    """
    Tokenizer class for compatibility with nlp_check.py
    """
    def __init__(self, model_name=None):
        self.model_name = model_name or MODEL
        self.tokenizer = tokenizer  # Use the global tokenizer
    
    def tokenize(self, text, max_length=512, add_special_tokens=True):
        """Tokenize text using the configured tokenizer"""
        return tokenize(text, max_length, add_special_tokens)
    
    def encode(self, text, **kwargs):
        """Encode text to token IDs"""
        return self.tokenize(text, **kwargs)
    
    def decode(self, token_ids, **kwargs):
        """Decode token IDs back to text"""
        if self.tokenizer:
            try:
                return self.tokenizer.decode(token_ids, **kwargs)
            except Exception as e:
                logger.warning(f"[TOKENIZER] Decode failed: {e}")
        
        # Fallback: just return the token IDs as string
        return " ".join(map(str, token_ids))


# Export for backward compatibility
__all__ = ["tokenize", "clean_text", "Tokenizer", "tokenizer"]

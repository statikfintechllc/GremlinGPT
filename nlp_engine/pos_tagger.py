#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: Module Integrity Directive
# This script is a component of the GremlinGPT system, under Alpha expansion.

# Import NLP environment globals
from conda_envs.environments.nlp.globals import *

# Import shared lazy loading utilities
from .lazy_utils import get_memory_functions, conditional_execute

import os
try:
    import nltk
    from nltk import pos_tag, word_tokenize
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    nltk = pos_tag = word_tokenize = None
    
from datetime import datetime

def lazy_import_utils():
    """Lazy import utils functionality to prevent circular dependencies"""
    try:
        from utils.logging_config import setup_module_logger
        from utils.nltk_setup import setup_nltk_data
        return setup_module_logger, setup_nltk_data
    except ImportError as e:
        logger.warning(f"Utils functions not available: {e}")
        return lambda x, y: logger, lambda: os.path.expanduser("~/nltk_data")

# Get functions lazily
# Get memory functions using shared utility
embed_text, package_embedding, inject_watermark = get_memory_functions()
setup_module_logger, setup_nltk_data = lazy_import_utils()

# Initialize module-specific logger
try:
    logger_instance = setup_module_logger("nlp_engine", "pos_tagger")
except:
    logger_instance = logger  # Use global logger as fallback

# ─────────────────────────────────────────────────────────────
# Init
# ─────────────────────────────────────────────────────────────

WATERMARK = "source:GremlinGPT"
ORIGIN = "pos_tagger"

# Ensure nltk resources are prepped and paths registered
if HAS_NLTK:
    nltk_path = setup_nltk_data()

    # Download POS tagger to project directory only
    try:
        nltk.data.find("taggers/averaged_perceptron_tagger")
        print(f"[NLTK] Found POS tagger in {nltk_path}")
    except LookupError:
        print(f"[NLTK] Downloading POS tagger to {nltk_path}")
        nltk.download("averaged_perceptron_tagger", download_dir=nltk_path, quiet=True)
else:
    print("[NLTK] NLTK not available, using fallback POS tagging")

# ─────────────────────────────────────────────────────────────
# POS Tagging
# ─────────────────────────────────────────────────────────────

def get_pos_tags(text):
    """
    Performs part-of-speech tagging on input text.
    Logs metadata and embeds summary in vector memory.
    """
    if not HAS_NLTK:
        logger.warning("NLTK not available, returning basic POS tags")
        # Simple fallback POS tagging
        tokens = text.split()
        tags = []
        for token in tokens:
            if token.isalpha():
                if token.endswith('ing'):
                    tags.append((token, 'VERB'))
                elif token.endswith('ed'):
                    tags.append((token, 'VERB'))
                elif token.endswith('ly'):
                    tags.append((token, 'ADV'))
                else:
                    tags.append((token, 'NOUN'))
            elif token.isdigit():
                tags.append((token, 'NUM'))
            else:
                tags.append((token, 'PUNCT'))
        return tags
    
    try:
        tokens = word_tokenize(text)
        tags = pos_tag(tokens)

        summary = f"POS tagging: {len(tokens)} tokens | Example: {tags[:3]}"
        
        # Use utility function for conditional execution with memory functions
        def store_embedding():
            vector = embed_text(summary)
            package_embedding(
                text=summary,
                vector=vector,
                meta={
                    "origin": ORIGIN,
                    "timestamp": datetime.utcnow().isoformat(),
                    "token_count": len(tokens),
                    "watermark": WATERMARK,
                },
            )
            inject_watermark(origin=ORIGIN)
        
        conditional_execute(
            (embed_text, package_embedding, inject_watermark),
            store_embedding
        )
        
        return tags

    except Exception as e:
        logger.error(f"[POS_TAGGER] Failed to tag input: {e}")
        return []

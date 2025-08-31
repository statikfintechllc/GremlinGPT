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

import os
import nltk
from nltk import pos_tag, word_tokenize
from datetime import datetime

# For cross-environment communication, use lazy loading
def lazy_import_memory():
    """Lazy import memory functionality to prevent circular dependencies"""
    try:
        from memory.vector_store.embedder import embed_text, package_embedding, inject_watermark
        return embed_text, package_embedding, inject_watermark
    except ImportError as e:
        logger.warning(f"Memory functions not available: {e}")
        return None, None, None

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
embed_text, package_embedding, inject_watermark = lazy_import_memory()
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
nltk_path = setup_nltk_data()

# Download POS tagger to project directory only
try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
    print(f"[NLTK] Found POS tagger in {nltk_path}")
except LookupError:
    print(f"[NLTK] Downloading POS tagger to {nltk_path}")
    nltk.download("averaged_perceptron_tagger", download_dir=nltk_path, quiet=True)

# ─────────────────────────────────────────────────────────────
# POS Tagging
# ─────────────────────────────────────────────────────────────

def get_pos_tags(text):
    """
    Performs part-of-speech tagging on input text.
    Logs metadata and embeds summary in vector memory.
    """
    try:
        tokens = word_tokenize(text)
        tags = pos_tag(tokens)

        summary = f"POS tagging: {len(tokens)} tokens | Example: {tags[:3]}"
        
        if embed_text and package_embedding and inject_watermark:
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
        
        return tags

    except Exception as e:
        logger.error(f"[POS_TAGGER] Failed to tag input: {e}")
        return []

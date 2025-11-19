# !/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: Module Integrity Directive
# This script is a component of the GremlinGPT system, under Alpha expansion.

# Import scraper environment globals
from conda_envs.environments.scraper.globals import *

# Use relative imports within scraper environment
from .dom_navigator import extract_dom_structure


# For cross-environment communication (memory), use lazy loading
def lazy_import_memory():
    """Lazy import memory functionality to prevent circular dependencies"""
    try:
        from memory.vector_store.embedder import (
            embed_text,
            package_embedding,
            inject_watermark,
        )

        return embed_text, package_embedding, inject_watermark
    except ImportError as e:
        logger.warning(f"Memory functions not available: {e}")
        return None, None, None


# Get memory functions lazily
embed_text, package_embedding, inject_watermark = lazy_import_memory()

from utils.logging_config import setup_module_logger

# Initialize module-specific logger
logger = setup_module_logger("scraper", "page_simulator")
from datetime import datetime

WATERMARK = "source:GremlinGPT"
ORIGIN = "page_simulator"


def store_scrape_to_memory(url, html):
    """
    Extracts DOM metadata from scraped HTML and stores a vectorized summary in memory.
    """
    try:
        structure = extract_dom_structure(html)
        summary_text = f"[{url}]\n{structure.get('text', '')}"
        vector = embed_text(summary_text)

        package_embedding(
            text=summary_text,
            vector=vector,
            meta={
                "origin": ORIGIN,
                "type": "scrape_snapshot",
                "url": url,
                "timestamp": datetime.utcnow().isoformat(),
                "watermark": WATERMARK,
            },
        )

        inject_watermark(origin=ORIGIN)
        logger.info(f"[{ORIGIN.upper()}] Stored scrape vector for: {url}")

    except Exception as e:
        logger.error(f"[{ORIGIN.upper()}] Failed to store scrape for {url}: {e}")

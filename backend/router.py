#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: Module Integrity Directive
# This script is a component of the GremlinGPT system, under Alpha expansion.

from environments.orchestrator import CFG, logger, resolve_path, DATA_DIR, MEM

def register_routes(app):
    logger.info("[ROUTER] Verifying and backing up API routes...")

    # Import handlers individually to avoid namespace conflicts
    routes = []
    try:
        from backend.api.chat_handler import chat
        routes.append(("/api/chat", chat, ["POST"]))
    except ImportError as e:
        logger.warning(f"[ROUTER] Could not import chat handler: {e}")
    
    try:
        from backend.api.memory_api import graph
        routes.append(("/api/memory/graph", graph, ["GET"]))
    except ImportError as e:
        logger.warning(f"[ROUTER] Could not import memory API: {e}")
    
    try:
        from backend.api.scraping_api import scrape_url
        routes.append(("/api/scrape", scrape_url, ["POST"]))
    except ImportError as e:
        logger.warning(f"[ROUTER] Could not import scraping API: {e}")
    
    try:
        from backend.api.planner import list_tasks, get_signals, set_task_priority
        routes.extend([
            ("/api/agent/tasks", list_tasks, ["GET"]),
            ("/api/trading/signals", get_signals, ["GET"]),
            ("/api/tasks/priority", set_task_priority, ["POST"]),
        ])
    except ImportError as e:
        logger.warning(f"[ROUTER] Could not import planner API: {e}")
    
    logger.info(f"[ROUTER] Found {len(routes)} route handlers available")

    # Build a set of existing route paths for efficient lookup
    existing_paths = {rule.rule for rule in app.url_map.iter_rules()}

    for path, handler, methods in routes:
        # Check if the route already exists (likely via blueprint)
        if path in existing_paths:
            logger.info(
                f"[ROUTER] Verified: {path} is already registered (likely via blueprint)."
            )
            # Optionally, backup/verify handler identity
            existing_rule = next((rule for rule in app.url_map.iter_rules() if rule.rule == path), None)
            if existing_rule and hasattr(existing_rule, "endpoint"):
                logger.debug(
                    f"[ROUTER] Existing endpoint for {path}: {existing_rule.endpoint}"
                )
        else:
            try:
                endpoint_name = f"{handler.__module__}.{handler.__name__}"
                app.add_url_rule(path, view_func=handler, methods=methods, endpoint=endpoint_name)
                app.add_url_rule(path, view_func=handler, methods=methods)
                logger.success(
                    f"[ROUTER] Route registered as backup: {path} -> {handler.__name__}"
                )
            except Exception as e:
                logger.error(f"[ROUTER] Backup registration failed for {path}: {e}")

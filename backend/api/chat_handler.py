#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# # GremlinGPT v1.0.3 :: Module Integrity Directive
# This script is a component of the GremlinGPT system, under Alpha expansion. v5 :: Module Integrity Directive

# Import orchestrator environment globals for backend
from conda_envs.environments.orchestrator.globals import *

# For cross-environment communication, use lazy loading
def lazy_import_flask():
    """Lazy import flask functionality to prevent circular dependencies"""
    try:
        from flask import request, jsonify, has_request_context

        return request, jsonify, has_request_context
    except ImportError as e:
        logger.warning(f"Flask functions not available: {e}")
        return None, None, None


def lazy_import_nlp():
    """Lazy import NLP functionality to prevent circular dependencies"""
    try:
        from nlp_engine.tokenizer import tokenize
        from nlp_engine.transformer_core import encode

        return tokenize, encode
    except ImportError as e:
        logger.warning(f"NLP functions not available: {e}")
        return None, None


def lazy_import_memory():
    """Lazy import memory functionality to prevent circular dependencies"""
    try:
        from memory.vector_store import embedder
        from memory.log_history import log_event

        return embedder, log_event
    except ImportError as e:
        logger.warning(f"Memory functions not available: {e}")
        return None, None


# Get cross-environment functions lazily
request, jsonify, has_request_context = lazy_import_flask()
tokenize, encode = lazy_import_nlp()
embedder, log_event = lazy_import_memory()

# Use relative imports within orchestrator environment
from agent_core.task_queue import enqueue_task
from backend.interface import commands
import sys
from pathlib import Path
import datetime
import os

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


from environments.dashboard import logger


def chat(user_input=None):
    if has_request_context():
        data = request.get_json()
        user_input = data.get("message", "").strip()
    elif user_input is not None:
        user_input = user_input.strip()
    else:
        logger.warning("[CHAT] No input provided to chat()")
        return {"error": "No input provided"}, 400

    if not user_input:
        logger.warning("[CHAT] Empty input received.")
        resp = {"error": "Empty input"}
        if has_request_context():
            return jsonify(resp), 400
        else:
            return resp, 400

    try:
        # Check if agents are running by looking for the PID file
        import os

        agent_pid_file = project_root / "run" / "agents.pid"

        if agent_pid_file.exists():
            with open(agent_pid_file, "r") as f:
                agent_pid = f.read().strip()

            # Check if the process is actually running
            try:
                os.kill(int(agent_pid), 0)  # Signal 0 checks if process exists
                agent_status = "active"
                logger.info(f"[CHAT] Agents are running (PID: {agent_pid})")
            except (OSError, ValueError):
                agent_status = "inactive"
                logger.warning(f"[CHAT] Agent PID file exists but process not running")
        else:
            agent_status = "inactive"
            logger.warning(f"[CHAT] No agent PID file found")

        # Process with available systems
        tokens = tokenize(user_input)
        vector = encode(user_input)
        task = commands.parse_command(user_input)
        result = commands.execute_command(task)

        # Log the interaction
        embedder.package_embedding(
            text=user_input,
            vector=vector,
            meta={
                "origin": "chat_handler",
                "type": task.get("type", "unknown"),
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "user_input": user_input,
                "agent_status": agent_status,
                "watermark": "source:GremlinGPT",
            },
        )
        log_event(
            "chat",
            "processed",
            {
                "input": user_input,
                "task_type": task.get("type", "unknown"),
                "agent_status": agent_status,
            },
        )

        # If agents are active, provide enhanced response
        if agent_status == "active":
            # Enqueue task for agent processing
            if task["type"] == "unknown":
                enqueue_task({"type": "nlp", "text": user_input})
            else:
                enqueue_task(task)

            response = {
                "response": f"GremlinGPT agents processed your message. Command interpreted as: {task['type']}",
                "tokens": tokens,
                "result": result,
                "status": "active",
                "agent_status": "running",
                "timestamp": datetime.datetime.utcnow().isoformat(),
            }
        else:
            # Fallback processing
            if task["type"] == "unknown":
                logger.warning(f"[CHAT] Fallback processing for: {user_input}")

            response = {
                "response": f"Processed with limited services. Command interpreted as: {task['type']}",
                "tokens": tokens,
                "result": result,
                "status": "degraded",
                "note": "Core agent services not fully active",
                "timestamp": datetime.datetime.utcnow().isoformat(),
            }

    except Exception as e:
        logger.error(f"[CHAT] Error processing message: {e}")
        import traceback

        logger.error(traceback.format_exc())

        response = {
            "response": f"Error processing message: {str(e)}",
            "status": "error",
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }

    # Return Flask response if inside a request, else tuple for CLI
    return (jsonify(response), 200) if has_request_context() else (response, 200)

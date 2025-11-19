#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# core/globals_orchestrator.py
# ORCHESTRATOR ENVIRONMENT GLOBALS
# For gremlin-orchestrator conda environment

# ========================================================================================
# STANDARD LIBRARY IMPORTS
# ========================================================================================
import os
import sys
import json
import time
import logging
import asyncio
import threading
import pathlib
import datetime
import subprocess
import traceback
import signal
import uuid
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

# ========================================================================================
# ORCHESTRATOR SPECIFIC IMPORTS
# ========================================================================================
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("[ORCHESTRATOR] NumPy not available")

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("[ORCHESTRATOR] PyYAML not available")

try:
    from loguru import logger

    HAS_LOGURU = True
except ImportError:
    HAS_LOGURU = False
    import logging as logger

    print("[ORCHESTRATOR] Loguru not available, using standard logging")

try:
    import click

    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    print("[ORCHESTRATOR] Click not available")

try:
    import rich
    from rich.console import Console
    from rich.logging import RichHandler

    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None
    print("[ORCHESTRATOR] Rich not available")

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("[ORCHESTRATOR] psutil not available")

try:
    import schedule

    HAS_SCHEDULE = True
except ImportError:
    HAS_SCHEDULE = False
    print("[ORCHESTRATOR] schedule not available")

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    print("[ORCHESTRATOR] watchdog not available")

try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("[ORCHESTRATOR] networkx not available")

try:
    import toml

    HAS_TOML = True
except ImportError:
    HAS_TOML = False
    print("[ORCHESTRATOR] TOML not available")


# ========================================================================================
# CONFIGURATION MANAGEMENT
# ========================================================================================
def load_config():
    """Load configuration for orchestrator environment"""
    config_path = Path(__file__).parent.parent / "config" / "config.toml"
    if config_path.exists() and HAS_TOML:
        try:
            return toml.load(config_path)
        except Exception as e:
            print(f"[ORCHESTRATOR] Error loading config: {e}")
            return get_default_orchestrator_config()
    else:
        return get_default_orchestrator_config()


def get_default_orchestrator_config():
    """Default configuration for orchestrator"""
    return {
        "system": {"debug": True, "environment": "development"},
        "orchestrator": {
            "loop_interval": 1.0,
            "task_timeout": 300,
            "max_concurrent_tasks": 5,
        },
        "core": {"snapshot_interval": 60, "checkpoint_interval": 300},
        "fsm": {"port": 8003, "states": ["idle", "thinking", "acting", "learning"]},
    }


# Load configuration
CFG = load_config()


# ========================================================================================
# LOGGING SETUP
# ========================================================================================
def setup_orchestrator_logging():
    """Setup logging for orchestrator environment"""
    log_dir = Path(__file__).parent.parent / "data" / "logs" / "core"
    log_dir.mkdir(parents=True, exist_ok=True)

    if HAS_LOGURU:
        logger.add(
            log_dir / "orchestrator.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO",
            format="{time} | {level} | {module}:{function}:{line} | {message}",
        )
        return logger
    else:
        handlers = []
        if HAS_RICH:
            handlers.append(RichHandler(console=console))
        handlers.append(logging.FileHandler(log_dir / "orchestrator.log"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=handlers,
        )
        return logging.getLogger("orchestrator")


logger = setup_orchestrator_logging()


# ========================================================================================
# PATH UTILITIES
# ========================================================================================
def resolve_path(relative_path: str) -> Path:
    """Resolve relative path from GremlinGPT root"""
    base_path = Path(__file__).parent.parent
    return base_path / relative_path


# Common paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = DATA_DIR / "logs"
CONFIG_DIR = PROJECT_ROOT / "config"
CHECKPOINT_DIR = PROJECT_ROOT / "run" / "checkpoints"


# ========================================================================================
# CORE UTILITIES
# ========================================================================================
def get_task_queue_path():
    """Get task queue file path"""
    return CHECKPOINT_DIR / "task_queue.json"


def get_state_snapshot_path():
    """Get state snapshot file path"""
    return CHECKPOINT_DIR / "state_snapshot.json"


def load_task_queue():
    """Load task queue from checkpoint"""
    queue_path = get_task_queue_path()
    if queue_path.exists():
        try:
            with open(queue_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading task queue: {e}")
            return {"tasks": [], "current_task": None}
    return {"tasks": [], "current_task": None}


def save_task_queue(queue_data):
    """Save task queue to checkpoint"""
    queue_path = get_task_queue_path()
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(queue_path, "w") as f:
            json.dump(queue_data, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving task queue: {e}")


# ========================================================================================
# EXPORT COMMON SYMBOLS
# ========================================================================================
__all__ = [
    # Configuration
    "CFG",
    "load_config",
    "get_default_orchestrator_config",
    # Logging
    "logger",
    "setup_orchestrator_logging",
    # Paths
    "resolve_path",
    "PROJECT_ROOT",
    "DATA_DIR",
    "LOG_DIR",
    "CONFIG_DIR",
    "CHECKPOINT_DIR",
    # Task management
    "load_task_queue",
    "save_task_queue",
    "get_task_queue_path",
    "get_state_snapshot_path",
    # Feature flags
    "HAS_NUMPY",
    "HAS_YAML",
    "HAS_RICH",
    "HAS_PSUTIL",
    "HAS_SCHEDULE",
    "HAS_WATCHDOG",
    "HAS_NETWORKX",
    # Standard imports
    "os",
    "sys",
    "json",
    "time",
    "asyncio",
    "threading",
    "Path",
    "datetime",
    "uuid",
]

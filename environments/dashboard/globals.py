#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# Dashboard Environment Globals - gremlin-dashboard conda environment
# Handles: Flask, API endpoints, web interface, configuration management

# ========================================================================================
# STANDARD LIBRARY IMPORTS
# ========================================================================================
import os
import sys
import json
import time
import logging
import datetime
from datetime import datetime as dt, timezone, timedelta
import pathlib
import traceback
import uuid

# Import bulletproof logger
try:
    from utils.logging_config import setup_module_logger
    logger = setup_module_logger("dashboard")
except ImportError:
    # Fallback to standard logging
    logger = logging.getLogger("dashboard")
    # Add success method to avoid attribute errors
    def success(msg):
        logger.info(f"SUCCESS: {msg}")
    logger.success = success
from pathlib import Path
import asyncio

# ========================================================================================
# DASHBOARD-SPECIFIC IMPORTS (Flask, Web APIs)
# ========================================================================================

# Flask and web framework
try:
    import flask
    from flask import Flask, request, jsonify, send_from_directory
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    flask = Flask = request = jsonify = send_from_directory = None

# Socket.IO for real-time communication
try:
    import socketio
    from flask_socketio import SocketIO, emit
    HAS_SOCKETIO = True
except ImportError:
    HAS_SOCKETIO = False
    socketio = SocketIO = emit = None

# Configuration management
try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False
    toml = None

# HTTP requests for API calls
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None

# JSON Web Tokens for authentication
try:
    import jwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False
    jwt = None

# ========================================================================================
# PATH CONFIGURATION
# ========================================================================================

# Get base project directory
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
CONFIG_FILE = BASE_DIR / "config" / "config.toml"
DATA_DIR = BASE_DIR / "data"
LOG_FILE = DATA_DIR / "logs" / "dashboard.log"

# Storage paths for backend compatibility
VECTOR_STORE_PATH = BASE_DIR / "memory" / "vector_store"
MEMORY_DB_PATH = BASE_DIR / "memory" / "memory.json"
FAISS_INDEX_PATH = BASE_DIR / "memory" / "vector_store" / "faiss"
FAISS_PATH = FAISS_INDEX_PATH  # Backend compatibility alias
CHROMA_PATH = BASE_DIR / "memory" / "vector_store" / "chroma"  # ChromaDB storage path

# Ensure directories exist
os.makedirs(DATA_DIR / "logs", exist_ok=True)

# ========================================================================================
# CONFIGURATION LOADING
# ========================================================================================

def load_config():
    """Load configuration for dashboard environment"""
    if HAS_TOML and CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return toml.load(f)
        except Exception as e:
            print(f"[DASHBOARD] Failed to load config: {e}")
    
    # Default dashboard configuration
    return {
        "system": {"debug": True, "log_level": "INFO"},
        "backend": {"host": "0.0.0.0", "port": 8080},
        "frontend": {"host": "0.0.0.0", "port": 4321},
        "dashboard": {
            "title": "GremlinGPT Dashboard",
            "theme": "dark",
            "realtime_updates": True
        }
    }

CFG = load_config()

# ========================================================================================
# LOGGING SETUP
# ========================================================================================

logging.basicConfig(
    level=getattr(logging, CFG.get("system", {}).get("log_level", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

# logger already initialized above with bulletproof logger

# ========================================================================================
# SAFE IMPORT HELPERS
# ========================================================================================

def safe_import_function(module_name, function_name):
    """Safely import a function from a module"""
    try:
        module = __import__(module_name, fromlist=[function_name])
        return getattr(module, function_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"[DASHBOARD] Failed to import {function_name} from {module_name}: {e}")
        return None

def safe_import_class(module_name, class_name):
    """Safely import a class from a module"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"[DASHBOARD] Failed to import {class_name} from {module_name}: {e}")
        return None

# ========================================================================================
# DASHBOARD CONFIGURATION & MEMORY INIT
# ========================================================================================

BACKEND_CONFIG = CFG.get("backend", {})
FRONTEND_CONFIG = CFG.get("frontend", {})
DASHBOARD_CONFIG = CFG.get("dashboard", {})

# Backend settings
BACKEND_HOST = BACKEND_CONFIG.get("host", "0.0.0.0")
BACKEND_PORT = BACKEND_CONFIG.get("port", 8080)

# Frontend settings  
FRONTEND_HOST = FRONTEND_CONFIG.get("host", "0.0.0.0")
FRONTEND_PORT = FRONTEND_CONFIG.get("port", 4321)

# Dashboard settings
DASHBOARD_TITLE = DASHBOARD_CONFIG.get("title", "GremlinGPT Dashboard")
DASHBOARD_THEME = DASHBOARD_CONFIG.get("theme", "dark")
REALTIME_UPDATES = DASHBOARD_CONFIG.get("realtime_updates", True)

# Initialize MEM object for compatibility
MEM = {}

# ========================================================================================
# DASHBOARD UTILITY FUNCTIONS
# ========================================================================================

def extract_dom_structure(html_content):
    """Extract DOM structure - placeholder for dashboard compatibility"""
    logger.warning("[DASHBOARD] extract_dom_structure called - not implemented in dashboard environment")
    return {"error": "Function not available in dashboard environment"}

# Standard library re-export for compatibility
import sys

# ========================================================================================
# API HANDLER IMPORTS - DISABLED TO AVOID CIRCULAR IMPORTS
# ========================================================================================

# Import API handlers (these should be lightweight for dashboard env)
# Temporarily disabled to avoid circular imports during initial load
# chat_handler = safe_import_function('backend.api.chat_handler', 'chat')
# memory_api = safe_import_function('backend.api.memory_api', 'graph')  
# planner_api = safe_import_function('backend.api.planner', 'list_tasks')
# scraping_api = safe_import_function('backend.api.scraping_api', 'route_scraping')

chat_handler = None
memory_api = None
planner_api = None
scraping_api = None

# ========================================================================================
# UTILITIES
# ========================================================================================

def resolve_path(path_str):
    """Resolve relative paths to absolute paths"""
    if not path_str:
        return BASE_DIR
    
    path = pathlib.Path(path_str)
    if path.is_absolute():
        return path
    return BASE_DIR / path

def get_system_status():
    """Get basic system status for dashboard"""
    return {
        "status": "online",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": "dashboard",
        "config_loaded": bool(CFG),
        "flask_available": HAS_FLASK,
        "socketio_available": HAS_SOCKETIO
    }

# ========================================================================================
# EXPORTS
# ========================================================================================

__all__ = [
    # Standard library
    'os', 'sys', 'json', 'time', 'logging', 'datetime', 'dt', 'timezone', 'timedelta', 'pathlib', 'traceback', 'uuid', 'Path', 'asyncio',
    
    # Configuration
    'CFG', 'BASE_DIR', 'DATA_DIR', 'LOG_FILE', 'MEM',
    'BACKEND_HOST', 'BACKEND_PORT', 'FRONTEND_HOST', 'FRONTEND_PORT',
    'DASHBOARD_TITLE', 'DASHBOARD_THEME', 'REALTIME_UPDATES',
    
    # Storage paths
    'VECTOR_STORE_PATH', 'MEMORY_DB_PATH', 'FAISS_INDEX_PATH', 'FAISS_PATH', 'CHROMA_PATH',
    
    # Flask and web framework
    'flask', 'Flask', 'request', 'jsonify', 'send_from_directory',
    'socketio', 'SocketIO', 'emit',
    
    # HTTP and requests
    'requests', 'jwt',
    
    # Configuration management
    'toml', 'load_config',
    
    # Utilities
    'logger', 'resolve_path', 'get_system_status',
    'safe_import_function', 'safe_import_class',
    'extract_dom_structure',
    
    # API handlers
    'chat_handler', 'memory_api', 'planner_api', 'scraping_api',
    
    # Availability flags
    'HAS_FLASK', 'HAS_SOCKETIO', 'HAS_TOML', 'HAS_REQUESTS', 'HAS_JWT'
]

logger.info(f"[DASHBOARD] Dashboard environment globals loaded successfully. {len(__all__)} items exported.")

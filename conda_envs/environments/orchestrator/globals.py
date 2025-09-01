#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# Orchestrator Environment Globals - gremlin-orchestrator conda environment  
# Handles: Core orchestration, agent coordination, task management, system control

# ========================================================================================
# STANDARD LIBRARY IMPORTS
# ========================================================================================
import os
import sys
import json
import time
import logging
import datetime
import pathlib
from pathlib import Path
import traceback
import shutil
import threading
import multiprocessing
import subprocess
import signal
import queue
import asyncio
import concurrent.futures

# Import bulletproof logger
try:
    from utils.logging_config import setup_module_logger
    logger = setup_module_logger("orchestrator")
except ImportError:
    # Fallback to standard logging
    logger = logging.getLogger("orchestrator")
    # Add success method to avoid attribute errors
    def success(msg):
        logger.info(f"SUCCESS: {msg}")
    logger.success = success

# ========================================================================================
# ORCHESTRATOR-SPECIFIC IMPORTS
# ========================================================================================

# Async and concurrency
try:
    import asyncio
    import aiohttp
    import aiofiles
    HAS_ASYNC = True
except ImportError:
    HAS_ASYNC = False
    asyncio = aiohttp = aiofiles = None

# Task scheduling and queuing
try:
    import celery
    from celery import Celery
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False
    celery = Celery = None

try:
    import rq
    from rq import Queue, Worker
    HAS_RQ = True
except ImportError:
    HAS_RQ = False
    rq = Queue = Worker = None

# Process management
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None

# Configuration management
try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False
    toml = None

# State machines
try:
    import transitions
    from transitions import Machine
    HAS_TRANSITIONS = True
except ImportError:
    HAS_TRANSITIONS = False
    transitions = Machine = None

# Agent communication
try:
    import zmq
    HAS_ZMQ = True
except ImportError:
    HAS_ZMQ = False
    zmq = None

# Monitoring and observability
try:
    import prometheus_client
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    prometheus_client = None

# ========================================================================================
# PATH CONFIGURATION
# ========================================================================================

# Get base project directory
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
CONFIG_FILE = BASE_DIR / "config" / "config.toml"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
TASKS_DIR = DATA_DIR / "tasks"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
PID_DIR = BASE_DIR / "run"
LOG_FILE = LOGS_DIR / "orchestrator.log"

# System files
PID_FILE = PID_DIR / "orchestrator.pid"
STATE_FILE = DATA_DIR / "orchestrator_state.json"

# Ensure directories exist
for directory in [LOGS_DIR, TASKS_DIR, SNAPSHOTS_DIR, PID_DIR]:
    os.makedirs(directory, exist_ok=True)

# ========================================================================================
# CONFIGURATION LOADING
# ========================================================================================

def load_config():
    """Load configuration for orchestrator environment"""
    if HAS_TOML and CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return toml.load(f)
        except Exception as e:
            print(f"[ORCHESTRATOR] Failed to load config: {e}")
    
    # Default orchestrator configuration
    return {
        "system": {"debug": True, "log_level": "INFO"},
        "orchestrator": {
            "max_workers": 4,
            "task_timeout": 300,
            "heartbeat_interval": 30,
            "max_retries": 3,
            "enable_snapshots": True,
            "snapshot_interval": 3600,
            "agent_startup_delay": 5
        },
        "agents": {
            "data_analyst": {"enabled": True, "priority": 1},
            "trading_strategist": {"enabled": True, "priority": 2},
            "learning_agent": {"enabled": True, "priority": 3},
            "planner": {"enabled": True, "priority": 4}
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
# ORCHESTRATOR CONFIGURATION
# ========================================================================================

ORCHESTRATOR_CONFIG = CFG.get("orchestrator", {})
AGENTS_CONFIG = CFG.get("agents", {})

# Orchestrator settings
MAX_WORKERS = ORCHESTRATOR_CONFIG.get("max_workers", 4)
TASK_TIMEOUT = ORCHESTRATOR_CONFIG.get("task_timeout", 300)
HEARTBEAT_INTERVAL = ORCHESTRATOR_CONFIG.get("heartbeat_interval", 30)
MAX_RETRIES = ORCHESTRATOR_CONFIG.get("max_retries", 3)
ENABLE_SNAPSHOTS = ORCHESTRATOR_CONFIG.get("enable_snapshots", True)
SNAPSHOT_INTERVAL = ORCHESTRATOR_CONFIG.get("snapshot_interval", 3600)
AGENT_STARTUP_DELAY = ORCHESTRATOR_CONFIG.get("agent_startup_delay", 5)

# Agent configurations
# Handle different config formats - if agents is dict with enabled=true, use default agents
if isinstance(AGENTS_CONFIG, dict) and AGENTS_CONFIG.get("enabled") and "types" in AGENTS_CONFIG:
    # Use agents.types format
    agent_configs = {agent_type["name"]: agent_type for agent_type in AGENTS_CONFIG.get("types", [])}
    ENABLED_AGENTS = [name for name, config in agent_configs.items() if config.get("enabled", True)]
    AGENT_PRIORITIES = {name: config.get("priority", 5) for name, config in agent_configs.items()}
elif isinstance(AGENTS_CONFIG, dict) and not AGENTS_CONFIG.get("enabled", True):
    # Agents disabled
    ENABLED_AGENTS = []
    AGENT_PRIORITIES = {}
else:
    # Fallback to default agent list
    ENABLED_AGENTS = ["data_analyst", "trading_strategist", "learning_agent", "planner"]
    AGENT_PRIORITIES = {"data_analyst": 1, "trading_strategist": 2, "learning_agent": 3, "planner": 4}

# ========================================================================================
# SAFE IMPORT HELPERS
# ========================================================================================

def safe_import_function(module_name, function_name):
    """Safely import a function from a module"""
    try:
        module = __import__(module_name, fromlist=[function_name])
        return getattr(module, function_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"[ORCHESTRATOR] Failed to import {function_name} from {module_name}: {e}")
        return None

def safe_import_class(module_name, class_name):
    """Safely import a class from a module"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"[ORCHESTRATOR] Failed to import {class_name} from {module_name}: {e}")
        return None

# ========================================================================================
# PROCESS MANAGEMENT
# ========================================================================================

def write_pid_file():
    """Write current process ID to file"""
    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"[ORCHESTRATOR] PID {os.getpid()} written to {PID_FILE}")
        return True
    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Failed to write PID file: {e}")
        return False

def read_pid_file():
    """Read process ID from file"""
    try:
        if PID_FILE.exists():
            with open(PID_FILE, 'r') as f:
                return int(f.read().strip())
    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Failed to read PID file: {e}")
    return None

def is_process_running(pid):
    """Check if a process is running"""
    if not pid:
        return False
    
    if HAS_PSUTIL:
        return psutil.pid_exists(pid)
    else:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

def cleanup_pid_file():
    """Remove PID file"""
    try:
        if PID_FILE.exists():
            os.remove(PID_FILE)
            logger.info("[ORCHESTRATOR] PID file cleaned up")
    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Failed to cleanup PID file: {e}")

# ========================================================================================
# STATE MANAGEMENT
# ========================================================================================

def save_state(state_data):
    """Save orchestrator state to file"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state_data, f, indent=2, default=str)
        logger.debug("[ORCHESTRATOR] State saved successfully")
        return True
    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Failed to save state: {e}")
        return False

def load_state():
    """Load orchestrator state from file"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Failed to load state: {e}")
    
    # Return default state
    return {
        "status": "stopped",
        "start_time": None,
        "last_heartbeat": None,
        "active_agents": [],
        "task_queue_size": 0
    }

# ========================================================================================
# CORE SYSTEM IMPORTS - DISABLED TO AVOID CIRCULAR IMPORTS
# ========================================================================================

# Import core system components
# Temporarily disabled to avoid circular imports during initial load
# orchestrator = safe_import_class('core.orchestrator', 'Orchestrator')
# kernel = safe_import_class('core.kernel', 'Kernel')
# loop = safe_import_class('core.loop', 'MainLoop')
# scheduler = safe_import_class('backend.scheduler', 'Scheduler')
# state_manager = safe_import_class('backend.state_manager', 'StateManager')

# Import agent coordinator
# agent_coordinator = safe_import_class('agents.agent_coordinator', 'AgentCoordinator')

# Import agent core components
# task_queue = safe_import_class('agent_core.task_queue', 'TaskQueue')
# fsm = safe_import_class('agent_core.fsm', 'FiniteStateMachine')

orchestrator = None
kernel = None
loop = None
scheduler = None
state_manager = None
agent_coordinator = None
task_queue = None
fsm = None

# Initialize MEM, LOOP and other compatibility objects
MEM = {}
LOOP = None
MODELS_DIR = BASE_DIR / "models"
METADATA_DB_PATH = DATA_DIR / "metadata.db"

# ========================================================================================
# UTILITIES
# ========================================================================================

def resolve_path(path_str):
    """Resolve relative paths to absolute paths"""
    if not path_str:
        return BASE_DIR
    
    # Handle variable expansion
    if "$ROOT" in path_str:
        path_str = path_str.replace("$ROOT", str(BASE_DIR))
    
    path = pathlib.Path(path_str)
    if path.is_absolute():
        return path
    return BASE_DIR / path

def get_system_info():
    """Get basic system information"""
    info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "pid": os.getpid(),
        "python_version": sys.version,
        "platform": sys.platform
    }
    
    if HAS_PSUTIL:
        try:
            info.update({
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent
            })
        except Exception:
            pass
    
    return info

def get_orchestrator_status():
    """Get orchestrator environment status"""
    return {
        "status": "online",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": "orchestrator",
        "config_loaded": bool(CFG),
        "async_available": HAS_ASYNC,
        "celery_available": HAS_CELERY,
        "rq_available": HAS_RQ,
        "psutil_available": HAS_PSUTIL,
        "transitions_available": HAS_TRANSITIONS,
        "zmq_available": HAS_ZMQ,
        "prometheus_available": HAS_PROMETHEUS,
        "max_workers": MAX_WORKERS,
        "enabled_agents": ENABLED_AGENTS,
        "pid_file_exists": PID_FILE.exists(),
        "state_file_exists": STATE_FILE.exists()
    }

# ========================================================================================
# EXPORTS
# ========================================================================================

__all__ = [
    # Configuration
    'CFG', 'BASE_DIR', 'DATA_DIR', 'LOGS_DIR', 'TASKS_DIR', 
    'SNAPSHOTS_DIR', 'PID_DIR', 'LOG_FILE', 'MEM', 'LOOP',
    'PID_FILE', 'STATE_FILE', 'MODELS_DIR', 'METADATA_DB_PATH',
    'MAX_WORKERS', 'TASK_TIMEOUT', 'HEARTBEAT_INTERVAL', 'MAX_RETRIES',
    'ENABLE_SNAPSHOTS', 'SNAPSHOT_INTERVAL', 'AGENT_STARTUP_DELAY',
    'ENABLED_AGENTS', 'AGENT_PRIORITIES',
    
    # Standard library
    'os', 'sys', 'json', 'time', 'logging', 'datetime', 'threading', 'multiprocessing', 'subprocess', 'signal', 'queue',
    'concurrent', 'pathlib', 'Path', 'shutil', 'traceback',
    
    # Async and concurrency
    'asyncio', 'aiohttp', 'aiofiles',
    
    # Task management
    'celery', 'Celery', 'rq', 'Queue', 'Worker',
    
    # Process management
    'psutil',
    
    # Configuration management
    'toml', 'load_config',
    
    # State machines
    'transitions', 'Machine',
    
    # Communication
    'zmq',
    
    # Monitoring
    'prometheus_client',
    
    # Core system components
    'orchestrator', 'kernel', 'loop', 'scheduler', 'state_manager',
    'agent_coordinator', 'task_queue', 'fsm',
    
    # Process management functions
    'write_pid_file', 'read_pid_file', 'is_process_running', 'cleanup_pid_file',
    
    # State management functions
    'save_state', 'load_state',
    
    # Environment health checks
    'check_environment_health', 'get_required_modules', 'check_dependencies',
    
    # Utilities
    'logger', 'resolve_path', 'get_system_info', 'get_orchestrator_status',
    'safe_import_function', 'safe_import_class',
    
    # Availability flags
    'HAS_ASYNC', 'HAS_CELERY', 'HAS_RQ', 'HAS_PSUTIL', 'HAS_TRANSITIONS',
    'HAS_ZMQ', 'HAS_PROMETHEUS', 'HAS_TOML'
]

# ========================================================================================
# ENVIRONMENT HEALTH CHECK FUNCTIONS
# ========================================================================================

def get_required_modules():
    """Get list of required modules for orchestrator environment"""
    return [
        'asyncio', 'threading', 'multiprocessing', 'subprocess', 'signal', 'queue',
        'concurrent.futures', 'psutil', 'transitions', 'zmq', 'prometheus_client'
    ]

def check_dependencies():
    """Check if all required dependencies are available"""
    import importlib
    required = get_required_modules()
    available = {}
    
    for module in required:
        try:
            importlib.import_module(module)
            available[module] = True
        except ImportError:
            available[module] = False
            logger.warning(f"Missing dependency: {module}")
    
    return available

def check_environment_health():
    """Verify orchestrator environment dependencies are loaded"""
    dependencies = check_dependencies()
    failed = [mod for mod, status in dependencies.items() if not status]
    
    if failed:
        logger.error(f"Orchestrator environment health check failed. Missing: {failed}")
        return False
    else:
        logger.info("Orchestrator environment health check passed")
        return True

# Write PID file on import
write_pid_file()

logger.info(f"[ORCHESTRATOR] Orchestrator environment globals loaded successfully. {len(__all__)} items exported.")

#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# Memory Environment Globals - gremlin-memory conda environment
# Handles: Memory management, graph databases, knowledge graphs, embeddings storage

# ========================================================================================
# STANDARD LIBRARY IMPORTS
# ========================================================================================
import os
import sys
import json
import time
import logging
import datetime
from datetime import datetime, timezone, timedelta
import pathlib
from pathlib import Path
import traceback
import pickle
import sqlite3
import hashlib

# Import bulletproof logger
try:
    from utils.logging_config import setup_module_logger
    logger = setup_module_logger("memory")
except ImportError:
    # Fallback to standard logging
    logger = logging.getLogger("memory")
    # Add success method to avoid attribute errors
    def success(msg):
        logger.info(f"SUCCESS: {msg}")
    logger.success = success

# ========================================================================================
# MEMORY-SPECIFIC IMPORTS
# ========================================================================================

# Graph databases
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None

try:
    import neo4j
    from neo4j import GraphDatabase
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False
    neo4j = GraphDatabase = None

# Vector databases
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    faiss = None

try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    chromadb = None

try:
    import pinecone
    HAS_PINECONE = True
except ImportError:
    HAS_PINECONE = False
    pinecone = None

# Data processing and embeddings
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

# Serialization and caching
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    redis = None

# Configuration management
try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False
    toml = None

# UUID for unique identifiers
try:
    import uuid
    HAS_UUID = True
except ImportError:
    HAS_UUID = False
    uuid = None

# ========================================================================================
# PATH CONFIGURATION
# ========================================================================================

# Get base project directory
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
CONFIG_FILE = BASE_DIR / "config" / "config.toml"
DATA_DIR = BASE_DIR / "data"
MEMORY_DIR = DATA_DIR / "memory"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
GRAPHS_DIR = DATA_DIR / "graphs"
CACHE_DIR = DATA_DIR / "cache"
LOG_FILE = DATA_DIR / "logs" / "memory.log"

# Memory files
MEMORY_JSON = BASE_DIR / "config" / "memory.json"
GRAPH_DB_PATH = MEMORY_DIR / "knowledge_graph.db"
EMBEDDINGS_INDEX = EMBEDDINGS_DIR / "faiss_index.bin"

# Ensure directories exist
for directory in [MEMORY_DIR, EMBEDDINGS_DIR, GRAPHS_DIR, CACHE_DIR, DATA_DIR / "logs"]:
    os.makedirs(directory, exist_ok=True)

# ========================================================================================
# CONFIGURATION LOADING
# ========================================================================================

def load_config():
    """Load configuration for memory environment"""
    if HAS_TOML and CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return toml.load(f)
        except Exception as e:
            print(f"[MEMORY] Failed to load config: {e}")
    
    # Default memory configuration
    return {
        "system": {"debug": True, "log_level": "INFO"},
        "memory": {
            "graph_db": "networkx",
            "vector_db": "faiss",
            "embedding_dimension": 384,
            "max_memory_entries": 10000,
            "cache_ttl": 3600,
            "enable_persistence": True
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
# MEMORY CONFIGURATION
# ========================================================================================

MEMORY_CONFIG = CFG.get("memory", {})

# Database settings
GRAPH_DB_TYPE = MEMORY_CONFIG.get("graph_db", "networkx")
VECTOR_DB_TYPE = MEMORY_CONFIG.get("vector_db", "faiss")
EMBEDDING_DIMENSION = MEMORY_CONFIG.get("embedding_dimension", 384)
MAX_MEMORY_ENTRIES = MEMORY_CONFIG.get("max_memory_entries", 10000)
CACHE_TTL = MEMORY_CONFIG.get("cache_ttl", 3600)
ENABLE_PERSISTENCE = MEMORY_CONFIG.get("enable_persistence", True)

# ========================================================================================
# SAFE IMPORT HELPERS
# ========================================================================================

def safe_import_function(module_name, function_name):
    """Safely import a function from a module"""
    try:
        module = __import__(module_name, fromlist=[function_name])
        return getattr(module, function_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"[MEMORY] Failed to import {function_name} from {module_name}: {e}")
        return None

def safe_import_class(module_name, class_name):
    """Safely import a class from a module"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"[MEMORY] Failed to import {class_name} from {module_name}: {e}")
        return None

# ========================================================================================
# MEMORY SYSTEM INITIALIZATION
# ========================================================================================

def initialize_graph_db():
    """Initialize the graph database"""
    if GRAPH_DB_TYPE == "networkx" and HAS_NETWORKX:
        try:
            graph = nx.DiGraph()
            logger.info("[MEMORY] Initialized NetworkX graph database")
            return graph
        except Exception as e:
            logger.error(f"[MEMORY] Failed to initialize NetworkX: {e}")
    
    elif GRAPH_DB_TYPE == "neo4j" and HAS_NEO4J:
        try:
            # This would need actual Neo4j connection details
            logger.info("[MEMORY] Neo4j driver available")
            return None  # Would return actual driver
        except Exception as e:
            logger.error(f"[MEMORY] Failed to initialize Neo4j: {e}")
    
    return None

def initialize_vector_db():
    """Initialize the vector database"""
    if VECTOR_DB_TYPE == "faiss" and HAS_FAISS:
        try:
            if EMBEDDINGS_INDEX.exists():
                index = faiss.read_index(str(EMBEDDINGS_INDEX))
                logger.info("[MEMORY] Loaded existing FAISS index")
            else:
                index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
                logger.info(f"[MEMORY] Created new FAISS index (dim={EMBEDDING_DIMENSION})")
            return index
        except Exception as e:
            logger.error(f"[MEMORY] Failed to initialize FAISS: {e}")
    
    elif VECTOR_DB_TYPE == "chromadb" and HAS_CHROMADB:
        try:
            client = chromadb.Client()
            collection = client.get_or_create_collection("gremlin_memory")
            logger.info("[MEMORY] Initialized ChromaDB collection")
            return collection
        except Exception as e:
            logger.error(f"[MEMORY] Failed to initialize ChromaDB: {e}")
    
    return None

def load_memory_json():
    """Load existing memory from JSON file"""
    if MEMORY_JSON.exists():
        try:
            with open(MEMORY_JSON, 'r') as f:
                memory_data = json.load(f)
            logger.info(f"[MEMORY] Loaded {len(memory_data)} memory entries from JSON")
            return memory_data
        except Exception as e:
            logger.error(f"[MEMORY] Failed to load memory JSON: {e}")
    
    return {}

# Initialize memory systems
GRAPH_DB = initialize_graph_db()
VECTOR_DB = initialize_vector_db()
MEMORY_DATA = load_memory_json()

# ========================================================================================
# MEMORY SYSTEM IMPORTS
# ========================================================================================

# Import memory system components
memory_manager = safe_import_class('memory.memory_manager', 'MemoryManager')
graph_manager = safe_import_class('memory.graph_manager', 'GraphManager')
vector_store = safe_import_class('memory.vector_store', 'VectorStore')
knowledge_graph = safe_import_class('memory.knowledge_graph', 'KnowledgeGraph')

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

def generate_memory_id():
    """Generate a unique ID for memory entries"""
    if HAS_UUID:
        return str(uuid.uuid4())
    else:
        # Fallback to timestamp-based ID
        return f"mem_{int(time.time() * 1000000)}"

def hash_content(content):
    """Generate hash for content deduplication"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()

def save_memory_json(memory_data):
    """Save memory data to JSON file"""
    try:
        with open(MEMORY_JSON, 'w') as f:
            json.dump(memory_data, f, indent=2, default=str)
        logger.info(f"[MEMORY] Saved {len(memory_data)} memory entries to JSON")
        return True
    except Exception as e:
        logger.error(f"[MEMORY] Failed to save memory JSON: {e}")
        return False

def get_memory_status():
    """Get memory environment status"""
    return {
        "status": "online",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": "memory",
        "config_loaded": bool(CFG),
        "networkx_available": HAS_NETWORKX,
        "neo4j_available": HAS_NEO4J,
        "faiss_available": HAS_FAISS,
        "chromadb_available": HAS_CHROMADB,
        "numpy_available": HAS_NUMPY,
        "pandas_available": HAS_PANDAS,
        "redis_available": HAS_REDIS,
        "graph_db_initialized": GRAPH_DB is not None,
        "vector_db_initialized": VECTOR_DB is not None,
        "memory_entries_count": len(MEMORY_DATA),
        "graph_db_type": GRAPH_DB_TYPE,
        "vector_db_type": VECTOR_DB_TYPE
    }

# ========================================================================================
# MEMORY SYSTEM STATE
# ========================================================================================

# Global memory storage dictionary
MEM = {}

# ========================================================================================
# EXPORTS
# ========================================================================================

__all__ = [
    # Standard library
    'os', 'sys', 'json', 'time', 'logging', 'datetime', 'pathlib', 'Path', 'traceback', 'pickle', 'sqlite3', 'hashlib',
    
    # Configuration
    'CFG', 'BASE_DIR', 'DATA_DIR', 'MEMORY_DIR', 'EMBEDDINGS_DIR', 
    'GRAPHS_DIR', 'CACHE_DIR', 'LOG_FILE',
    'MEMORY_JSON', 'GRAPH_DB_PATH', 'EMBEDDINGS_INDEX',
    'GRAPH_DB_TYPE', 'VECTOR_DB_TYPE', 'EMBEDDING_DIMENSION', 
    'MAX_MEMORY_ENTRIES', 'CACHE_TTL', 'ENABLE_PERSISTENCE',
    
    # Memory state
    'MEM',
    
    # Graph databases
    'nx', 'neo4j', 'GraphDatabase',
    
    # Vector databases
    'faiss', 'chromadb', 'pinecone',
    
    # Data processing
    'np', 'pd',
    
    # Caching and serialization
    'redis',
    
    # Configuration management
    'toml', 'load_config',
    
    # Utilities
    'uuid',
    
    # Initialized systems
    'GRAPH_DB', 'VECTOR_DB', 'MEMORY_DATA',
    
    # Memory system components
    'memory_manager', 'graph_manager', 'vector_store', 'knowledge_graph',
    
    # Utilities
    'logger', 'resolve_path', 'generate_memory_id', 'hash_content',
    'save_memory_json', 'get_memory_status',
    'safe_import_function', 'safe_import_class',
    'initialize_graph_db', 'initialize_vector_db', 'load_memory_json',
    
    # Availability flags
    'HAS_NETWORKX', 'HAS_NEO4J', 'HAS_FAISS', 'HAS_CHROMADB', 
    'HAS_PINECONE', 'HAS_NUMPY', 'HAS_PANDAS', 'HAS_REDIS', 
    'HAS_TOML', 'HAS_UUID'
]

logger.info(f"[MEMORY] Memory environment globals loaded successfully. {len(__all__)} items exported.")

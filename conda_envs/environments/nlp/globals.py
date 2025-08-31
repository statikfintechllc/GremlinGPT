#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# NLP Environment Globals - gremlin-nlp conda environment
# Handles: Natural language processing, embeddings, language models, text analysis

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
import traceback
import re

# Import bulletproof logger
try:
    from utils.logging_config import setup_module_logger
    logger = setup_module_logger("nlp")
except ImportError:
    # Fallback to standard logging
    logger = logging.getLogger("nlp")
    # Add success method to avoid attribute errors
    def success(msg):
        logger.info(f"SUCCESS: {msg}")
    logger.success = success

# ========================================================================================
# NLP-SPECIFIC IMPORTS
# ========================================================================================

# Transformers and Hugging Face
try:
    import transformers
    from transformers import AutoTokenizer, AutoModel, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    transformers = AutoTokenizer = AutoModel = pipeline = None

# NLTK for text processing
try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    nltk = word_tokenize = sent_tokenize = stopwords = PorterStemmer = WordNetLemmatizer = None

# spaCy for advanced NLP
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False
    spacy = None

# Sentence transformers for embeddings
try:
    import sentence_transformers
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    sentence_transformers = None
    SentenceTransformer = None

# OpenAI API
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    openai = None

# Langchain for LLM orchestration
try:
    import langchain
    from langchain.llms import OpenAI
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    langchain = OpenAI = LLMChain = PromptTemplate = None

# Text processing utilities
try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False
    textstat = None

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

# Configuration management
try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False
    toml = None

# ========================================================================================
# PATH CONFIGURATION
# ========================================================================================

# Get base project directory
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
CONFIG_FILE = BASE_DIR / "config" / "config.toml"
DATA_DIR = BASE_DIR / "data"
NLP_DATA_DIR = DATA_DIR / "nlp_training_sets"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
NLTK_DATA_DIR = DATA_DIR / "nltk_data"
PROMPTS_DIR = DATA_DIR / "prompts"
LOG_FILE = DATA_DIR / "logs" / "nlp.log"

# Ensure directories exist
for directory in [NLP_DATA_DIR, EMBEDDINGS_DIR, NLTK_DATA_DIR, PROMPTS_DIR, DATA_DIR / "logs"]:
    os.makedirs(directory, exist_ok=True)

# Set NLTK data path
if HAS_NLTK:
    nltk.data.path.append(str(NLTK_DATA_DIR))

# ========================================================================================
# CONFIGURATION LOADING
# ========================================================================================

def load_config():
    """Load configuration for NLP environment"""
    if HAS_TOML and CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return toml.load(f)
        except Exception as e:
            print(f"[NLP] Failed to load config: {e}")
    
    # Default NLP configuration
    return {
        "system": {"debug": True, "log_level": "INFO"},
        "nlp": {
            "embedding_model": "all-MiniLM-L6-v2",
            "max_sequence_length": 512,
            "batch_size": 32,
            "vector_db": "faiss",
            "openai_model": "gpt-3.5-turbo"
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
# NLP CONFIGURATION
# ========================================================================================

NLP_CONFIG = CFG.get("nlp", {})

# Model settings
EMBEDDING_MODEL_NAME = NLP_CONFIG.get("embedding_model", "all-MiniLM-L6-v2")
MAX_SEQUENCE_LENGTH = NLP_CONFIG.get("max_sequence_length", 512)
BATCH_SIZE = NLP_CONFIG.get("batch_size", 32)
VECTOR_DB_TYPE = NLP_CONFIG.get("vector_db", "faiss")
OPENAI_MODEL = NLP_CONFIG.get("openai_model", "gpt-3.5-turbo")

# ========================================================================================
# SAFE IMPORT HELPERS
# ========================================================================================

def safe_import_function(module_name, function_name):
    """Safely import a function from a module"""
    try:
        module = __import__(module_name, fromlist=[function_name])
        return getattr(module, function_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"[NLP] Failed to import {function_name} from {module_name}: {e}")
        return None

def safe_import_class(module_name, class_name):
    """Safely import a class from a module"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"[NLP] Failed to import {class_name} from {module_name}: {e}")
        return None

# ========================================================================================
# NLP MODEL INITIALIZATION
# ========================================================================================

def initialize_embedding_model():
    """Initialize the sentence transformer model for embeddings"""
    if HAS_SENTENCE_TRANSFORMERS:
        try:
            model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info(f"[NLP] Loaded embedding model: {EMBEDDING_MODEL_NAME}")
            return model
        except Exception as e:
            logger.error(f"[NLP] Failed to load embedding model: {e}")
    return None

def initialize_nltk_resources():
    """Download and initialize required NLTK resources"""
    if not HAS_NLTK:
        return False
    
    resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
    for resource in resources:
        try:
            nltk.download(resource, download_dir=NLTK_DATA_DIR, quiet=True)
        except Exception as e:
            logger.warning(f"[NLP] Failed to download NLTK resource {resource}: {e}")
    
    return True

# Initialize models if available
EMBEDDING_MODEL = initialize_embedding_model()
NLTK_INITIALIZED = initialize_nltk_resources()

# ========================================================================================
# NLP ENGINE IMPORTS
# ========================================================================================

# Import NLP engine components (safe imports for optional dependencies)
text_processor = safe_import_class('nlp_engine.text_processor', 'TextProcessor')
embedding_generator = safe_import_class('nlp_engine.embedding_generator', 'EmbeddingGenerator')
sentiment_analyzer = safe_import_class('nlp_engine.sentiment_analyzer', 'SentimentAnalyzer')
entity_extractor = safe_import_class('nlp_engine.entity_extractor', 'EntityExtractor')

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

def clean_text(text):
    """Basic text cleaning utility"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\!\?\,\;\:]', '', text)
    # Strip and return
    return text.strip()

def get_nlp_status():
    """Get NLP environment status"""
    return {
        "status": "online",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": "nlp",
        "config_loaded": bool(CFG),
        "transformers_available": HAS_TRANSFORMERS,
        "nltk_available": HAS_NLTK,
        "spacy_available": HAS_SPACY,
        "sentence_transformers_available": HAS_SENTENCE_TRANSFORMERS,
        "openai_available": HAS_OPENAI,
        "langchain_available": HAS_LANGCHAIN,
        "embedding_model_loaded": EMBEDDING_MODEL is not None,
        "nltk_initialized": NLTK_INITIALIZED
    }

# ========================================================================================
# EXPORTS
# ========================================================================================

__all__ = [
    # Configuration
    'CFG', 'BASE_DIR', 'DATA_DIR', 'NLP_DATA_DIR', 'EMBEDDINGS_DIR', 
    'NLTK_DATA_DIR', 'PROMPTS_DIR', 'LOG_FILE',
    'EMBEDDING_MODEL_NAME', 'MAX_SEQUENCE_LENGTH', 'BATCH_SIZE', 
    'VECTOR_DB_TYPE', 'OPENAI_MODEL',
    
    # Standard library
    'os', 'sys', 'json', 'time', 'logging', 'datetime', 'pathlib', 'traceback', 're',
    
    # Transformers and Hugging Face
    'transformers', 'AutoTokenizer', 'AutoModel', 'pipeline',
    
    # NLTK
    'nltk', 'word_tokenize', 'sent_tokenize', 'stopwords', 
    'PorterStemmer', 'WordNetLemmatizer',
    
    # spaCy
    'spacy',
    
    # Sentence transformers
    'sentence_transformers', 'SentenceTransformer',
    
    # OpenAI and Langchain
    'openai', 'langchain', 'OpenAI', 'LLMChain', 'PromptTemplate',
    
    # Text processing
    'textstat',
    
    # Vector databases
    'faiss', 'chromadb',
    
    # Configuration management
    'toml', 'load_config',
    
    # Initialized models
    'EMBEDDING_MODEL', 'NLTK_INITIALIZED',
    
    # NLP engine components
    'text_processor', 'embedding_generator', 'sentiment_analyzer', 'entity_extractor',
    
    # Utilities
    'logger', 'resolve_path', 'clean_text', 'get_nlp_status',
    'safe_import_function', 'safe_import_class',
    'initialize_embedding_model', 'initialize_nltk_resources',
    
    # Availability flags
    'HAS_TRANSFORMERS', 'HAS_NLTK', 'HAS_SPACY', 'HAS_SENTENCE_TRANSFORMERS',
    'HAS_OPENAI', 'HAS_LANGCHAIN', 'HAS_TEXTSTAT', 'HAS_FAISS', 
    'HAS_CHROMADB', 'HAS_TOML'
]

logger.info(f"[NLP] NLP environment globals loaded successfully. {len(__all__)} items exported.")

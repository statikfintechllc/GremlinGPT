#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# Scraper Environment Globals - gremlin-scraper conda environment
# Handles: Web scraping, data extraction, API clients, trading data feeds

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
import urllib.parse
import urllib.request
import html
import csv

# Import bulletproof logger
try:
    from utils.logging_config import setup_module_logger
    logger = setup_module_logger("scraper")
except ImportError:
    # Fallback to standard logging
    logger = logging.getLogger("scraper")
    # Add success method to avoid attribute errors
    def success(msg):
        logger.info(f"SUCCESS: {msg}")
    logger.success = success

# ========================================================================================
# SCRAPER-SPECIFIC IMPORTS
# ========================================================================================

# Web scraping frameworks
try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = HTTPAdapter = Retry = None

try:
    import scrapy
    from scrapy.crawler import CrawlerProcess
    HAS_SCRAPY = True
except ImportError:
    HAS_SCRAPY = False
    scrapy = CrawlerProcess = None

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False
    webdriver = By = WebDriverWait = EC = ChromeOptions = None

# HTML parsing
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    BeautifulSoup = None

try:
    import lxml
    from lxml import html as lxml_html
    HAS_LXML = True
except ImportError:
    HAS_LXML = False
    lxml = lxml_html = None

# Data processing
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

# API clients for trading data
try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False
    yf = None

try:
    import alpha_vantage
    from alpha_vantage.timeseries import TimeSeries
    HAS_ALPHA_VANTAGE = True
except ImportError:
    HAS_ALPHA_VANTAGE = False
    alpha_vantage = TimeSeries = None

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False
    ccxt = None

# Rate limiting and caching
try:
    from ratelimit import limits, sleep_and_retry
    HAS_RATELIMIT = True
except ImportError:
    HAS_RATELIMIT = False
    limits = sleep_and_retry = None

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

# User agent randomization
try:
    from fake_useragent import UserAgent
    HAS_FAKE_USERAGENT = True
except ImportError:
    HAS_FAKE_USERAGENT = False
    UserAgent = None

# ========================================================================================
# PATH CONFIGURATION
# ========================================================================================

# Get base project directory
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
CONFIG_FILE = BASE_DIR / "config" / "config.toml"
DATA_DIR = BASE_DIR / "data"
SCRAPES_DIR = DATA_DIR / "raw_scrapes"
CACHE_DIR = DATA_DIR / "cache"
LOG_FILE = DATA_DIR / "logs" / "scraper.log"

# Scraper-specific data directories
TRADING_DATA_DIR = DATA_DIR / "trading_data"
WEB_DATA_DIR = DATA_DIR / "web_data"
API_CACHE_DIR = CACHE_DIR / "api_responses"

# Ensure directories exist
for directory in [SCRAPES_DIR, CACHE_DIR, TRADING_DATA_DIR, WEB_DATA_DIR, API_CACHE_DIR, DATA_DIR / "logs"]:
    os.makedirs(directory, exist_ok=True)

# ========================================================================================
# CONFIGURATION LOADING
# ========================================================================================

def load_config():
    """Load configuration for scraper environment"""
    if HAS_TOML and CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return toml.load(f)
        except Exception as e:
            print(f"[SCRAPER] Failed to load config: {e}")
    
    # Default scraper configuration
    return {
        "system": {"debug": True, "log_level": "INFO"},
        "scraper": {
            "max_concurrent": 5,
            "request_delay": 1.0,
            "timeout": 30,
            "max_retries": 3,
            "enable_caching": True,
            "cache_ttl": 3600,
            "user_agent_rotation": True,
            "respect_robots_txt": True
        },
        "trading_apis": {
            "alpha_vantage_key": "",
            "polygon_key": "",
            "enable_crypto": True,
            "rate_limit_per_minute": 60
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
# SCRAPER CONFIGURATION
# ========================================================================================

SCRAPER_CONFIG = CFG.get("scraper", {})
TRADING_APIS_CONFIG = CFG.get("trading_apis", {})

# Scraper settings
MAX_CONCURRENT = SCRAPER_CONFIG.get("max_concurrent", 5)
REQUEST_DELAY = SCRAPER_CONFIG.get("request_delay", 1.0)
TIMEOUT = SCRAPER_CONFIG.get("timeout", 30)
MAX_RETRIES = SCRAPER_CONFIG.get("max_retries", 3)
ENABLE_CACHING = SCRAPER_CONFIG.get("enable_caching", True)
CACHE_TTL = SCRAPER_CONFIG.get("cache_ttl", 3600)
USER_AGENT_ROTATION = SCRAPER_CONFIG.get("user_agent_rotation", True)
RESPECT_ROBOTS_TXT = SCRAPER_CONFIG.get("respect_robots_txt", True)

# Trading API settings
ALPHA_VANTAGE_KEY = TRADING_APIS_CONFIG.get("alpha_vantage_key", "")
POLYGON_KEY = TRADING_APIS_CONFIG.get("polygon_key", "")
ENABLE_CRYPTO = TRADING_APIS_CONFIG.get("enable_crypto", True)
RATE_LIMIT_PER_MINUTE = TRADING_APIS_CONFIG.get("rate_limit_per_minute", 60)

# ========================================================================================
# SAFE IMPORT HELPERS
# ========================================================================================

def safe_import_function(module_name, function_name):
    """Safely import a function from a module"""
    try:
        module = __import__(module_name, fromlist=[function_name])
        return getattr(module, function_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"[SCRAPER] Failed to import {function_name} from {module_name}: {e}")
        return None

def safe_import_class(module_name, class_name):
    """Safely import a class from a module"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"[SCRAPER] Failed to import {class_name} from {module_name}: {e}")
        return None

# ========================================================================================
# SCRAPER INITIALIZATION
# ========================================================================================

def initialize_session():
    """Initialize requests session with retries and headers"""
    if not HAS_REQUESTS:
        return None
    
    session = requests.Session()
    
    # Configure retries
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set timeout
    session.timeout = TIMEOUT
    
    # Set user agent
    if HAS_FAKE_USERAGENT and USER_AGENT_ROTATION:
        try:
            ua = UserAgent()
            session.headers.update({'User-Agent': ua.random})
        except Exception:
            session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; GremlinGPT/1.0)'})
    else:
        session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; GremlinGPT/1.0)'})
    
    logger.info("[SCRAPER] Initialized requests session with retries")
    return session

def initialize_selenium_driver():
    """Initialize Selenium WebDriver (Chrome)"""
    if not HAS_SELENIUM:
        return None
    
    try:
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        if USER_AGENT_ROTATION and HAS_FAKE_USERAGENT:
            try:
                ua = UserAgent()
                options.add_argument(f'--user-agent={ua.random}')
            except Exception:
                pass
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(TIMEOUT)
        logger.info("[SCRAPER] Initialized Selenium Chrome driver")
        return driver
    except Exception as e:
        logger.error(f"[SCRAPER] Failed to initialize Selenium driver: {e}")
        return None

# Initialize scraping tools
HTTP_SESSION = initialize_session()
SELENIUM_DRIVER = None  # Lazy initialize when needed

# ========================================================================================
# SCRAPER COMPONENT IMPORTS
# ========================================================================================

# Import scraper components
web_scraper = safe_import_class('scraper.web_scraper', 'WebScraper')
trading_data_scraper = safe_import_class('scraper.trading_data_scraper', 'TradingDataScraper')
api_client = safe_import_class('scraper.api_client', 'APIClient')
data_processor = safe_import_class('scraper.data_processor', 'DataProcessor')

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

def clean_url(url):
    """Clean and validate URL"""
    if not url:
        return None
    
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urllib.parse.urlparse(url)
        return urllib.parse.urlunparse(parsed)
    except Exception:
        return None

def extract_domain(url):
    """Extract domain from URL"""
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None

def rate_limited_request(url, **kwargs):
    """Make a rate-limited HTTP request"""
    if not HTTP_SESSION:
        return None
    
    try:
        time.sleep(REQUEST_DELAY)
        response = HTTP_SESSION.get(url, **kwargs)
        response.raise_for_status()
        return response
    except Exception as e:
        logger.error(f"[SCRAPER] Request failed for {url}: {e}")
        return None

def save_scrape_data(data, filename):
    """Save scraped data to file"""
    try:
        filepath = SCRAPES_DIR / filename
        
        if isinstance(data, (dict, list)):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        logger.info(f"[SCRAPER] Saved scrape data to {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"[SCRAPER] Failed to save scrape data: {e}")
        return None

def get_scraper_status():
    """Get scraper environment status"""
    return {
        "status": "online",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": "scraper",
        "config_loaded": bool(CFG),
        "requests_available": HAS_REQUESTS,
        "scrapy_available": HAS_SCRAPY,
        "selenium_available": HAS_SELENIUM,
        "bs4_available": HAS_BS4,
        "lxml_available": HAS_LXML,
        "pandas_available": HAS_PANDAS,
        "yfinance_available": HAS_YFINANCE,
        "alpha_vantage_available": HAS_ALPHA_VANTAGE,
        "ccxt_available": HAS_CCXT,
        "session_initialized": HTTP_SESSION is not None,
        "selenium_driver_initialized": SELENIUM_DRIVER is not None,
        "max_concurrent": MAX_CONCURRENT,
        "request_delay": REQUEST_DELAY,
        "caching_enabled": ENABLE_CACHING
    }

# ========================================================================================
# EXPORTS
# ========================================================================================

__all__ = [
    # Configuration
    'CFG', 'BASE_DIR', 'DATA_DIR', 'SCRAPES_DIR', 'CACHE_DIR', 'LOG_FILE',
    'TRADING_DATA_DIR', 'WEB_DATA_DIR', 'API_CACHE_DIR',
    'MAX_CONCURRENT', 'REQUEST_DELAY', 'TIMEOUT', 'MAX_RETRIES',
    'ENABLE_CACHING', 'CACHE_TTL', 'USER_AGENT_ROTATION', 'RESPECT_ROBOTS_TXT',
    'ALPHA_VANTAGE_KEY', 'POLYGON_KEY', 'ENABLE_CRYPTO', 'RATE_LIMIT_PER_MINUTE',
    
    # Standard library
    're', 'urllib', 'html', 'csv',
    
    # Web scraping
    'requests', 'HTTPAdapter', 'Retry', 'scrapy', 'CrawlerProcess',
    'webdriver', 'By', 'WebDriverWait', 'EC', 'ChromeOptions',
    
    # HTML parsing
    'BeautifulSoup', 'lxml', 'lxml_html',
    
    # Data processing
    'pd', 'np',
    
    # Trading APIs
    'yf', 'alpha_vantage', 'TimeSeries', 'ccxt',
    
    # Rate limiting and caching
    'limits', 'sleep_and_retry', 'redis',
    
    # Configuration management
    'toml', 'load_config',
    
    # User agent
    'UserAgent',
    
    # Initialized tools
    'HTTP_SESSION', 'SELENIUM_DRIVER',
    
    # Scraper components
    'web_scraper', 'trading_data_scraper', 'api_client', 'data_processor',
    
    # Utilities
    'logger', 'resolve_path', 'clean_url', 'extract_domain',
    'rate_limited_request', 'save_scrape_data', 'get_scraper_status',
    'safe_import_function', 'safe_import_class',
    'initialize_session', 'initialize_selenium_driver',
    
    # Availability flags
    'HAS_REQUESTS', 'HAS_SCRAPY', 'HAS_SELENIUM', 'HAS_BS4', 'HAS_LXML',
    'HAS_PANDAS', 'HAS_NUMPY', 'HAS_YFINANCE', 'HAS_ALPHA_VANTAGE', 'HAS_CCXT',
    'HAS_RATELIMIT', 'HAS_REDIS', 'HAS_TOML', 'HAS_FAKE_USERAGENT'
]

logger.info(f"[SCRAPER] Scraper environment globals loaded successfully. {len(__all__)} items exported.")

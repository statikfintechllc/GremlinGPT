#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: Bulletproof Logging Configuration

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Try to import loguru, fallback to standard logging if not available
try:
    from loguru import logger as loguru_logger

    HAS_LOGURU = True

    # Create a bridge between loguru and standard logging
    class LoguruHandler(logging.Handler):
        def emit(self, record):
            try:
                level = record.levelname
                if hasattr(loguru_logger, level.lower()):
                    getattr(loguru_logger, level.lower())(record.getMessage())
                else:
                    loguru_logger.info(record.getMessage())
            except Exception:
                pass

except ImportError:
    HAS_LOGURU = False
    loguru_logger = None


# Create a unified logger that works with or without loguru
class BulletproofLogger:
    def __init__(self, name, log_file=None, level="INFO"):
        self.name = name
        self.level = getattr(logging, level.upper(), logging.INFO)

        # Set up standard logging
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)

        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(self.level)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            try:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                file_handler = logging.FileHandler(log_file, mode="a")
                file_handler.setLevel(self.level)
                file_formatter = logging.Formatter(
                    "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)

                # Set file permissions
                os.chmod(log_file, 0o644)
            except Exception as e:
                self.logger.warning(f"Could not set up file logging to {log_file}: {e}")

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def success(self, msg):
        self.logger.info(f"SUCCESS: {msg}")  # Fallback for loguru success

    def exception(self, msg):
        self.logger.exception(msg)


# Global logger instance
logger = BulletproofLogger("gremlin")

# Base logging directory - use project directory instead of home
project_root = Path(__file__).parent.parent
BASE_LOG_DIR = project_root / "data" / "logs"


def setup_module_logger(module_name, param2="INFO"):
    """
    Setup dedicated logger for a specific module

    Args:
        module_name (str): Name of the module (e.g., 'backend', 'nlp_engine', 'scraper')
        param2 (str): Either log_level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                     or submodule_name (for backward compatibility)

    Returns:
        BulletproofLogger: Configured logger instance
    """
    # Determine if param2 is a log level or submodule name
    valid_log_levels = [
        "TRACE",
        "DEBUG",
        "INFO",
        "SUCCESS",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]
    if param2.upper() in valid_log_levels:
        log_level = param2.upper()
        submodule = None
    else:
        # Backward compatibility: param2 is submodule name
        log_level = "INFO"
        submodule = param2

    # Ensure log directory exists
    module_log_dir = BASE_LOG_DIR / module_name
    module_log_dir.mkdir(parents=True, exist_ok=True)

    # Set proper permissions
    try:
        os.chmod(str(module_log_dir), 0o755)
    except Exception:
        pass

    # Configure module-specific log file (include submodule if provided)
    if submodule:
        log_file = module_log_dir / f"{module_name}_{submodule}.log"
        logger_name = f"{module_name}.{submodule}"
    else:
        log_file = module_log_dir / f"{module_name}.log"
        logger_name = module_name

    # Create bulletproof logger
    module_logger = BulletproofLogger(logger_name, str(log_file), log_level)
    module_logger.info(
        f"[LOGGING] Module logger initialized for {module_name} -> {log_file}"
    )

    return module_logger


def get_module_logger(module_name, log_level="INFO"):
    """
    Get or create a logger for a specific module

    Args:
        module_name (str): Name of the module
        log_level (str): Logging level

    Returns:
        BulletproofLogger: Configured logger instance
    """
    return setup_module_logger(module_name, log_level)


def create_all_module_loggers():
    """
    Create loggers for all major system modules
    """
    modules = [
        "backend",
        "nlp_engine",
        "memory",
        "scraper",
        "agents",
        "trading_core",
        "tools",
        "core",
        "executors",
        "self_training",
        "self_mutation_watcher",
        "utils",
        "tests",
        "frontend",
    ]

    for module in modules:
        setup_module_logger(module)

    logger.success(f"[LOGGING] Initialized loggers for {len(modules)} modules")


if __name__ == "__main__":
    create_all_module_loggers()

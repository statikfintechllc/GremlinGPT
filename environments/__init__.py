#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

"""
GremlinGPT Environments Module

This module provides environment-specific globals and acts as a proxy
to the actual environment globals located in conda_envs/environments/
"""

import os
import sys
from pathlib import Path

# Get the project root directory
_current_dir = Path(__file__).parent
_project_root = _current_dir.parent
_conda_envs_path = _project_root / "conda_envs"

# Add paths for proper imports
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_conda_envs_path) not in sys.path:
    sys.path.insert(0, str(_conda_envs_path))


def lazy_import(module_name):
    """Lazy import to prevent circular dependencies"""
    import importlib

    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")
        return None


# Environment module getters with lazy loading
def get_dashboard():
    """Get dashboard environment globals"""
    return lazy_import("conda_envs.environments.dashboard.globals")


def get_memory():
    """Get memory environment globals"""
    return lazy_import("conda_envs.environments.memory.globals")


def get_nlp():
    """Get NLP environment globals"""
    return lazy_import("conda_envs.environments.nlp.globals")


def get_orchestrator():
    """Get orchestrator environment globals"""
    return lazy_import("conda_envs.environments.orchestrator.globals")


def get_scraper():
    """Get scraper environment globals"""
    return lazy_import("conda_envs.environments.scraper.globals")


# Environment health check
def check_environment_health():
    """Verify all environment dependencies are available"""
    environments = {
        "dashboard": get_dashboard(),
        "memory": get_memory(),
        "nlp": get_nlp(),
        "orchestrator": get_orchestrator(),
        "scraper": get_scraper(),
    }

    health_status = {}
    all_healthy = True

    for env_name, env_module in environments.items():
        if env_module is None:
            health_status[env_name] = False
            all_healthy = False
        else:
            # Try to call environment-specific health check if available
            try:
                if hasattr(env_module, "check_environment_health"):
                    health_status[env_name] = env_module.check_environment_health()
                else:
                    health_status[env_name] = True
            except Exception as e:
                print(f"Health check failed for {env_name}: {e}")
                health_status[env_name] = False
                all_healthy = False

    return {
        "all_healthy": all_healthy,
        "environment_status": health_status,
        "summary": f"{'✅ All environments healthy' if all_healthy else '❌ Some environments have issues'}",
    }


def wait_for_environment_ready(env_name, timeout=30):
    """Wait for a specific environment to be ready"""
    import time

    start_time = time.time()

    while time.time() - start_time < timeout:
        env_func = {
            "dashboard": get_dashboard,
            "memory": get_memory,
            "nlp": get_nlp,
            "orchestrator": get_orchestrator,
            "scraper": get_scraper,
        }.get(env_name)

        if env_func and env_func() is not None:
            print(f"Environment {env_name} is ready")
            return True

        time.sleep(1)

    print(f"Timeout waiting for environment {env_name}")
    return False


__all__ = [
    "get_dashboard",
    "get_memory",
    "get_nlp",
    "get_orchestrator",
    "get_scraper",
    "check_environment_health",
    "wait_for_environment_ready",
    "lazy_import",
]

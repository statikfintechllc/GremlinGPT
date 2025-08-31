#!/usr/bin/env python3
"""Orchestrator Environment Proxy - redirects to conda_envs/environments/orchestrator/globals.py"""

import sys
from pathlib import Path

# Add conda_envs to path
_project_root = Path(__file__).parent.parent.parent
_conda_envs_path = _project_root / "conda_envs"
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_conda_envs_path) not in sys.path:
    sys.path.insert(0, str(_conda_envs_path))

# Import all orchestrator globals
try:
    from conda_envs.environments.orchestrator.globals import *
    orchestrator_available = True
except ImportError as e:
    print(f"Warning: Could not import orchestrator globals: {e}")
    orchestrator_available = False

__all__ = ['orchestrator_available']
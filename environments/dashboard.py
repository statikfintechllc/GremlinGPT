#!/usr/bin/env python3
"""Dashboard Environment Proxy - redirects to conda_envs/environments/dashboard/globals.py"""

import sys
from pathlib import Path

# Add conda_envs to path
_project_root = Path(__file__).parent.parent.parent
_conda_envs_path = _project_root / "conda_envs"
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_conda_envs_path) not in sys.path:
    sys.path.insert(0, str(_conda_envs_path))

# Import all dashboard globals
try:
    from conda_envs.environments.dashboard.globals import *

    dashboard_available = True
except ImportError as e:
    print(f"Warning: Could not import dashboard globals: {e}")
    dashboard_available = False

__all__ = ["dashboard_available"]

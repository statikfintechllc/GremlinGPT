# GremlinGPT self_training package

# Import NLP environment globals for self-training
from conda_envs.environments.nlp.globals import *

# Add lazy loading pattern for self-training components
def lazy_import(module_name):
    """Lazy import to prevent circular dependencies"""
    import importlib

    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")
        return None

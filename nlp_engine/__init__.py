# GremlinGPT NLP Engine package

# Import NLP environment globals
from conda_envs.environments.nlp.globals import *


# Add lazy loading pattern for NLP components
def lazy_import(module_name):
    """Lazy import to prevent circular dependencies"""
    import importlib

    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")
        return None

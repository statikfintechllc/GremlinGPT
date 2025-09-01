#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: Lazy Loading Utilities
# Shared utility functions to eliminate code duplication for lazy imports

from conda_envs.environments.nlp.globals import logger

def create_lazy_loader(module_path, *function_names):
    """Create a lazy loader function that safely imports functions from a module.
    
    This utility pattern eliminates code duplication for conditional imports
    throughout the codebase.
    
    Args:
        module_path (str): The module path to import from
        *function_names: Variable number of function names to import
        
    Returns:
        callable: A function that returns a tuple of functions or None values
    """
    def lazy_loader():
        try:
            module = __import__(module_path, fromlist=function_names)
            return tuple(getattr(module, name, None) for name in function_names)
        except ImportError as e:
            logger.warning(f"Functions not available from {module_path}: {e}")
            return tuple(None for _ in function_names)
    return lazy_loader

def conditional_execute(functions, callback, *args, **kwargs):
    """Execute callback only if all functions are available.
    
    Args:
        functions (tuple): Tuple of functions to check
        callback (callable): Function to execute if all functions are available
        *args, **kwargs: Arguments to pass to callback
        
    Returns:
        Result of callback or None if functions not available
    """
    if all(func is not None for func in functions):
        try:
            return callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing conditional callback: {e}")
            return None
    else:
        logger.debug("Skipping execution - required functions not available")
        return None

def safe_execute_with_fallback(primary_functions, fallback_functions, callback, *args, **kwargs):
    """Execute callback with primary functions, falling back to alternatives if needed.
    
    Args:
        primary_functions (tuple): Primary functions to try first
        fallback_functions (tuple): Fallback functions if primary fails
        callback (callable): Function to execute
        *args, **kwargs: Arguments to pass to callback
        
    Returns:
        Result of callback or None if all functions fail
    """
    # Try primary functions first
    result = conditional_execute(primary_functions, callback, *args, **kwargs)
    if result is not None:
        return result
    
    # Fall back to alternative functions
    logger.debug("Primary functions failed, trying fallback functions")
    return conditional_execute(fallback_functions, callback, *args, **kwargs)

# Common lazy loaders for cross-environment communication
memory_loader = create_lazy_loader(
    'memory.vector_store.embedder', 
    'embed_text', 'package_embedding', 'inject_watermark'
)

history_loader = create_lazy_loader(
    'memory.log_history', 
    'log_event'
)

orchestrator_loader = create_lazy_loader(
    'agent_core.fsm', 
    'inject_task'
)

backend_loader = create_lazy_loader(
    'backend.api_bridge',
    'send_to_frontend'
)

def get_memory_functions():
    """Get memory functions with lazy loading"""
    return memory_loader()

def get_history_functions():
    """Get history functions with lazy loading"""
    return history_loader()

def get_orchestrator_functions():
    """Get orchestrator functions with lazy loading"""
    return orchestrator_loader()

def get_backend_functions():
    """Get backend functions with lazy loading"""
    return backend_loader()

# Convenience decorators
def requires_memory_functions(func):
    """Decorator that ensures memory functions are available before execution"""
    def wrapper(*args, **kwargs):
        embed_text, package_embedding, inject_watermark = get_memory_functions()
        if all(f is not None for f in [embed_text, package_embedding, inject_watermark]):
            return func(*args, **kwargs)
        else:
            logger.warning(f"Skipping {func.__name__} - memory functions not available")
            return None
    return wrapper

def requires_orchestrator_functions(func):
    """Decorator that ensures orchestrator functions are available before execution"""
    def wrapper(*args, **kwargs):
        inject_task, = get_orchestrator_functions()
        if inject_task is not None:
            return func(*args, **kwargs)
        else:
            logger.warning(f"Skipping {func.__name__} - orchestrator functions not available")
            return None
    return wrapper
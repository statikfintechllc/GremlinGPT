#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: backend/api/api_endpoints.py :: Module Integrity Directive
# This script is a component of the GremlinGPT system, under Alpha expansion.

# Flask imports - will be imported via globals when available
try:
    import flask
    from flask import Blueprint
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Create mock classes for non-Flask environments
    class Blueprint:
        def __init__(self, name, import_name):
            self.name = name
            self.import_name = import_name
            self.deferred_functions = []
        def route(self, rule, **options):
            def decorator(f):
                self.deferred_functions.append((rule, f, options))
                return f
            return decorator
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import everything from dashboard environment for centralized dependency management
from environments.dashboard import *

# Fix datetime import after environment import
from datetime import datetime

# Create API blueprint
api_blueprint = Blueprint('api', __name__)

# Session storage for chat functionality
_sessions = {}

# === CHAT ENDPOINTS ===
@api_blueprint.route("/api/chat", methods=["POST"])
def api_chat():
    """Chat endpoint using centralized imports"""
    data = flask.request.get_json()
    user_input = data.get("message", "")
    session_id = data.get("session_id")
    user_id = data.get("user_id", "api_user")
    feedback = data.get("feedback")
    
    # Use ChatSession from centralized imports
    if session_id and session_id in _sessions:
        session = _sessions[session_id]
    else:
        if ChatSession:
            session = ChatSession(user_id=user_id)
            _sessions[session.session_id] = session
            session_id = session.session_id
        else:
            return flask.jsonify({"error": "ChatSession not available"}), 500
    
    try:
        result = session.process_input(user_input, feedback=feedback)
        result["session_id"] = session_id
        return flask.jsonify(result)
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# === FSM OPERATIONS ===
@api_blueprint.route("/api/fsm/status", methods=["GET"])
def api_fsm_status():
    """Get FSM status using centralized imports"""
    try:
        if get_fsm_status:
            status = get_fsm_status()
            return flask.jsonify({"fsm_status": status})
        else:
            return flask.jsonify({"fsm_status": "not_available"})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@api_blueprint.route("/api/fsm/tick", methods=["POST"])
def api_fsm_tick():
    """Trigger FSM tick using centralized imports"""
    try:
        if fsm_loop:
            result = fsm_loop()
            return flask.jsonify({"tick_result": result})
        else:
            return flask.jsonify({"error": "FSM not available"}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# === TASK QUEUE & PLANNER ===
@api_blueprint.route("/api/agent/tasks", methods=["GET", "POST"])
def api_agent_tasks():
    """Task management using centralized imports"""
    try:
        if flask.request.method == "POST":
            task_data = flask.request.get_json()
            task_desc = task_data.get("task")
            if enqueue_task:
                result = enqueue_task(task_desc)
                return flask.jsonify({"enqueued": result})
            else:
                return flask.jsonify({"error": "Task queue not available"}), 500
        
        # GET request
        if get_all_tasks:
            tasks = get_all_tasks()
            return flask.jsonify({"tasks": tasks})
        else:
            return flask.jsonify({"tasks": []})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# === MEMORY GRAPH ===
@api_blueprint.route("/api/memory/graph", methods=["GET"])
def api_memory_graph():
    """Memory graph endpoint using centralized imports"""
    try:
        # Use graph function from centralized imports if available
        if graph:
            result = graph()
            return flask.jsonify(result)
        else:
            return flask.jsonify({"nodes": [], "edges": [], "message": "Memory graph not available"})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# === TRADING SIGNALS ===
@api_blueprint.route("/api/trading/signals", methods=["GET"])
def api_trading_signals():
    """Trading signals using centralized imports"""
    try:
        if generate_signals:
            signals = generate_signals()
            return flask.jsonify({"signals": signals})
        else:
            return flask.jsonify({"signals": [], "message": "Signal generator not available"})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# === SCRAPING ===
@api_blueprint.route("/api/scrape", methods=["POST"])
def api_scrape():
    """Scraping endpoint using centralized imports"""
    data = flask.request.get_json()
    url = data.get("url")
    if not url:
        return flask.jsonify({"error": "Missing 'url'"}), 400
    
    try:
        # Use scraping functions from centralized imports
        if route_scraping:
            result = route_scraping(url)
            return flask.jsonify({"scrape_result": result})
        else:
            return flask.jsonify({"error": "Scraper not available"}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# === STATE MANAGEMENT ===
@api_blueprint.route("/api/state/save", methods=["POST"])
def api_save_state():
    """Save state using centralized imports"""
    try:
        if save_state:
            result = save_state({})
            return flask.jsonify({"save_result": result})
        else:
            return flask.jsonify({"error": "State manager not available"}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@api_blueprint.route("/api/state/load", methods=["GET"])
def api_load_state():
    """Load state using centralized imports"""
    try:
        if load_state:
            result = load_state()
            return flask.jsonify({"load_result": result})
        else:
            return flask.jsonify({"error": "State manager not available"}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# === SYSTEM CONFIGURATION ===
@api_blueprint.route("/api/system/config", methods=["GET"])
def api_system_config():
    """System configuration using centralized imports"""
    try:
        # Use CFG from centralized imports
        return flask.jsonify(CFG)
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@api_blueprint.route("/api/system/backend_select", methods=["POST"])
def api_system_backend_select():
    """Backend selection using centralized imports"""
    data = flask.request.get_json()
    backend = data.get("backend", "")
    if backend not in ["faiss", "chromadb"]:
        return flask.jsonify({"error": "Invalid backend. Use 'faiss' or 'chromadb'"}), 400
    
    try:
        if set_dashboard_backend:
            result = set_dashboard_backend(backend)
            return flask.jsonify({"success": result})
        else:
            return flask.jsonify({"error": "Backend selection not available"}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# === UTILITY ENDPOINTS ===
@api_blueprint.route("/api/tools/text/summarize", methods=["POST"])
def api_tools_text_summarize():
    """Text summarization using centralized imports"""
    data = flask.request.get_json()
    text = data.get("text")
    if not text:
        return flask.jsonify({"error": "Missing 'text'"}), 400
    
    try:
        if summarize_text:
            summary = summarize_text(text)
            return flask.jsonify({"summary": summary})
        else:
            return flask.jsonify({"error": "Summarizer not available"}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# === HEALTH CHECK ===
@api_blueprint.route("/api/health", methods=["GET"])
def api_health():
    """Health check endpoint"""
    return flask.jsonify({
        "status": "healthy",
        "version": "1.0.3",
        "imports_available": {
            "chat_session": ChatSession is not None,
            "fsm": fsm_loop is not None,
            "task_queue": enqueue_task is not None,
            "memory": graph is not None,
            "trading": generate_signals is not None,
            "scraping": route_scraping is not None,
            "state": save_state is not None,
        }
    })


# === SYSTEM STATUS ===
@api_blueprint.route("/api/system/status", methods=["GET"])
def api_system_status():
    """Get real system status"""
    try:
        import psutil
        import glob
        
        # Check service PIDs
        service_pids = {}
        pid_files = glob.glob("/tmp/gremlin_*.pid")
        
        for pid_file in pid_files:
            service_name = os.path.basename(pid_file).replace("gremlin_", "").replace(".pid", "")
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                    if psutil.pid_exists(pid):
                        service_pids[service_name] = {"pid": pid, "status": "running"}
                    else:
                        service_pids[service_name] = {"pid": pid, "status": "dead"}
            except:
                service_pids[service_name] = {"status": "unknown"}
        
        # System resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return flask.jsonify({
            "system": "online",
            "services": service_pids,
            "memory": {
                "used": f"{memory.used // (1024**3)}GB",
                "total": f"{memory.total // (1024**3)}GB",
                "percent": memory.percent
            },
            "disk": {
                "free": f"{disk.free // (1024**3)}GB",
                "used": f"{disk.used // (1024**3)}GB",
                "percent": round(disk.percent, 1)
            },
            "last_updated": datetime.now().isoformat()
        })
    except Exception as e:
        return flask.jsonify({
            "system": "degraded",
            "error": str(e),
            "services": {},
            "last_updated": datetime.now().isoformat()
        })


# === AGENTS STATUS ===
@api_blueprint.route("/api/agents/status", methods=["GET"])
def api_agents_status():
    """Get real agent status"""
    try:
        # Check process status by looking for running processes
        import subprocess
        
        def check_process_running(process_name):
            try:
                result = subprocess.run(
                    ["pgrep", "-f", process_name], 
                    capture_output=True, 
                    text=True
                )
                return len(result.stdout.strip().split('\n')) > 0 if result.stdout.strip() else False
            except:
                return False
        
        agents_status = {
            "fsm_agent": {
                "status": "active" if check_process_running("agent_core.fsm") else "inactive",
                "state": "IDLE",
                "tasks": 0
            },
            "trading_agent": {
                "status": "active" if check_process_running("trading_strategist_agent") else "inactive", 
                "strategy": "None",
                "signals": 0
            },
            "scraper_agent": {
                "status": "active" if check_process_running("scraper.scraper_loop") else "inactive",
                "targets": 0,
                "last_scrape": None
            },
            "nlp_agent": {
                "status": "active" if check_process_running("nlp_engine") else "inactive",
                "model": "bert-base-uncased",
                "processing": 0
            },
            "memory_agent": {
                "status": "active" if check_process_running("memory") else "inactive",
                "vectors": 0,
                "embeddings": 0
            }
        }
        
        return flask.jsonify({
            "agents": agents_status,
            "total_active": sum(1 for agent in agents_status.values() if agent["status"] == "active"),
            "last_updated": datetime.now().isoformat()
        })
    except Exception as e:
        return flask.jsonify({
            "error": str(e),
            "agents": {},
            "last_updated": datetime.now().isoformat()
        })


# === MEMORY STATUS ===  
@api_blueprint.route("/api/memory/status", methods=["GET"])
def api_memory_status():
    """Get real memory system status"""
    try:
        # Check vector store files
        vector_store_status = {
            "vector_store": "unknown",
            "embeddings": 0,
            "documents": 0,
            "training_data": 0,
            "cache_size": "0MB"
        }
        
        try:
            # Check FAISS index
            faiss_path = resolve_path("$ROOT/memory/vector_store/faiss/faiss_index.index")
            if os.path.exists(faiss_path):
                file_size = os.path.getsize(faiss_path)
                vector_store_status["vector_store"] = "faiss"
                vector_store_status["cache_size"] = f"{file_size // (1024*1024)}MB"
        except:
            pass
            
        try:
            # Check documents directory
            docs_path = resolve_path("$ROOT/memory/local_index/documents/")
            if os.path.exists(docs_path):
                vector_store_status["documents"] = len(os.listdir(docs_path))
        except:
            pass
            
        try:
            # Check training sets
            training_path = resolve_path("$ROOT/data/nlp_training_sets/")
            if os.path.exists(training_path):
                vector_store_status["training_data"] = len([f for f in os.listdir(training_path) if f.endswith('.json')])
        except:
            pass
        
        return flask.jsonify(vector_store_status)
    except Exception as e:
        return flask.jsonify({
            "error": str(e),
            "vector_store": "error"
        })


# === CONFIGURATION MANAGEMENT ===
@api_blueprint.route("/api/config/get", methods=["GET"])  
def api_config_get():
    """Get current configuration"""
    try:
        return flask.jsonify({
            "config": CFG,
            "config_file": "config/config.toml",
            "last_updated": datetime.now().isoformat()
        })
    except Exception as e:
        return flask.jsonify({
            "error": str(e),
            "config": {}
        })


@api_blueprint.route("/api/config/set", methods=["POST"])
def api_config_set():
    """Update configuration"""
    try:
        data = flask.request.get_json()
        section = data.get("section")
        key = data.get("key") 
        value = data.get("value")
        
        if not all([section, key, value is not None]):
            return flask.jsonify({"error": "Missing section, key, or value"}), 400
            
        # Update in-memory config
        if section not in CFG:
            CFG[section] = {}
        CFG[section][key] = value
        
        # TODO: Write back to config file
        
        return flask.jsonify({
            "success": True,
            "updated": f"{section}.{key} = {value}",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return flask.jsonify({
            "error": str(e),
            "success": False
        }), 500


# === FILE SYSTEM ENDPOINTS (for Source Editor) ===
@api_blueprint.route("/api/tree", methods=["GET"])
def api_file_tree():
    """Get project file tree"""
    try:
        def build_tree(path, max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return None
                
            items = []
            try:
                for item in sorted(os.listdir(path)):
                    if item.startswith('.'):
                        continue
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        children = build_tree(item_path, max_depth, current_depth + 1)
                        items.append({
                            "name": item,
                            "type": "directory", 
                            "path": os.path.relpath(item_path, resolve_path("$ROOT")),
                            "children": children if children else []
                        })
                    else:
                        # Only include common code files
                        if item.endswith(('.py', '.js', '.ts', '.json', '.yaml', '.yml', '.toml', '.md', '.txt', '.sh')):
                            items.append({
                                "name": item,
                                "type": "file",
                                "path": os.path.relpath(item_path, resolve_path("$ROOT"))
                            })
            except PermissionError:
                pass
            return items
        
        root_path = resolve_path("$ROOT")
        tree = build_tree(root_path)
        
        return flask.jsonify({
            "tree": tree,
            "root": root_path
        })
    except Exception as e:
        return flask.jsonify({
            "error": str(e),
            "tree": []
        })


@api_blueprint.route("/api/files/<path:file_path>", methods=["GET"])
def api_get_file(file_path):
    """Get file contents"""
    try:
        full_path = os.path.join(resolve_path("$ROOT"), file_path)
        
        # Security check - ensure path is within project
        if not os.path.abspath(full_path).startswith(os.path.abspath(resolve_path("$ROOT"))):
            return flask.jsonify({"error": "Access denied"}), 403
            
        if not os.path.exists(full_path):
            return flask.jsonify({"error": "File not found"}), 404
            
        if os.path.isdir(full_path):
            return flask.jsonify({"error": "Path is a directory"}), 400
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with latin-1 for binary files
            with open(full_path, 'r', encoding='latin-1') as f:
                content = f.read()
                
        return flask.jsonify({
            "content": content,
            "path": file_path,
            "size": os.path.getsize(full_path),
            "modified": datetime.fromtimestamp(os.path.getmtime(full_path)).isoformat()
        })
    except Exception as e:
        return flask.jsonify({
            "error": str(e)
        }), 500


@api_blueprint.route("/api/files/<path:file_path>", methods=["POST"])
def api_save_file(file_path):
    """Save file contents"""
    try:
        data = flask.request.get_json()
        content = data.get("content", "")
        
        full_path = os.path.join(resolve_path("$ROOT"), file_path)
        
        # Security check - ensure path is within project
        if not os.path.abspath(full_path).startswith(os.path.abspath(resolve_path("$ROOT"))):
            return flask.jsonify({"error": "Access denied"}), 403
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return flask.jsonify({
            "success": True,
            "path": file_path,
            "size": len(content.encode('utf-8')),
            "saved_at": datetime.now().isoformat()
        })
    except Exception as e:
        return flask.jsonify({
            "error": str(e),
            "success": False
        }), 500


# Export the blueprint for registration
__all__ = ['api_blueprint']
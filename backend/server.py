#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: Module Integrity Directive

# Add project root to Python path for environment imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CRITICAL: Eventlet monkey patching MUST happen before any other imports
HAS_EVENTLET = False
HAS_SOCKETIO = False
try:
    import eventlet
    eventlet.monkey_patch()
    HAS_EVENTLET = True
except ImportError:
    print("[SERVER] eventlet not available, continuing without async support")

# Import Flask and other dependencies
try:
    from flask import Flask, send_from_directory
    HAS_FLASK = True
except ImportError:
    print("[SERVER] Flask not available, server cannot start")
    exit(1)

try:
    from flask_socketio import SocketIO
    HAS_SOCKETIO = True
except ImportError:
    print("[SERVER] flask_socketio not available, continuing without WebSocket support")
    SocketIO = None

# Create Flask app
app = Flask(__name__)

# Set up SocketIO with or without eventlet
if HAS_SOCKETIO:
    if HAS_EVENTLET:
        socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
    else:
        socketio = SocketIO(app, cors_allowed_origins="*")

# Import and register API blueprints
try:
    from backend.api.agent_status import agent_status_bp
    app.register_blueprint(agent_status_bp)
    print("[SERVER] Agent status API registered")
except ImportError as e:
    print(f"[SERVER] Warning: Could not register agent status API: {e}")
    print("[SERVER] SocketIO initialized")
else:
    socketio = None
    print("[SERVER] Running without SocketIO support")

from environments.dashboard import CFG, logger, resolve_path, DATA_DIR

# Import and register API blueprint
try:
    from backend.api.api_endpoints import api_blueprint
    app.register_blueprint(api_blueprint)
    print("[SERVER] API endpoints registered")
except Exception as e:
    print(f"[SERVER] Failed to register API endpoints: {e}")

try:
    from backend.router import register_routes
    register_routes(app)
    logger.info("[SERVER] Additional routes registered")
except Exception as e:
    logger.warning(f"[SERVER] Could not register additional routes: {e}")
    # Continue without additional routes - API endpoints are already registered

# Broadcast function for system status
def broadcast_status(msg):
    try:
        if socketio:
            socketio.emit("system_broadcast", {"status": msg})
        logger.info(f"[BROADCAST] {msg}")
    except Exception as e:
        logger.error(f"[BROADCAST] Broadcast failed: {e}")

# Base API Checkpoint
@app.route("/")
def serve_index():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory("../frontend", filename)


# Chat API endpoint
@app.route('/api/nlp/chat', methods=['POST'])
def chat_endpoint():
    try:
        from flask import request, jsonify
        import datetime
        
        # Import the real chat handler
        try:
            from backend.api.chat_handler import chat
            logger.info("[CHAT] Using integrated GremlinGPT chat handler")
            
            # Use the real chat handler
            result = chat()
            
            # Handle different return types from chat handler
            if isinstance(result, tuple):
                response_data, status_code = result
                
                # Check if response_data is a Flask Response object
                if hasattr(response_data, 'get_json'):
                    # It's a Flask Response, extract the JSON
                    response_data = response_data.get_json()
                elif hasattr(response_data, 'json'):
                    # It's already JSON data
                    response_data = response_data
                
                if status_code != 200:
                    return jsonify(response_data), status_code
            else:
                # Single return value, assume it's a Flask Response
                if hasattr(result, 'get_json'):
                    return result  # Return the Flask Response directly
                else:
                    response_data = result
                    status_code = 200
            
            # Ensure response_data is a dictionary
            if not isinstance(response_data, dict):
                response_data = {"response": str(response_data)}
            
            # Ensure we have the right format for the frontend
            if 'response' not in response_data:
                response_data['response'] = response_data.get('result', 'Processed by GremlinGPT')
            
            response_data['timestamp'] = datetime.datetime.now().isoformat()
            response_data['status'] = 'success'
            
            logger.info(f"[CHAT] GremlinGPT processed message successfully")
            return jsonify(response_data)
            
        except ImportError as ie:
            logger.warning(f"[CHAT] Could not import chat handler: {ie}")
            # Fallback to echo
            data = request.get_json()
            message = data.get('message', '')
            
            if not message:
                return jsonify({'error': 'No message provided'}), 400
            
            logger.info(f"[CHAT] Fallback echo for message: {message}")
            response = f"Echo (core services not running): {message}"
            
            return jsonify({
                'response': response,
                'status': 'degraded',
                'note': 'Core GremlinGPT services not active - using fallback mode',
                'timestamp': datetime.datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"[CHAT] Error processing message: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


# Health check endpoint
@app.route('/health')
def health_check():
    try:
        from flask import jsonify
        return jsonify({
            'status': 'healthy',
            'services': {
                'flask': True,
                'socketio': HAS_SOCKETIO,
                'eventlet': HAS_EVENTLET
            }
        })
    except Exception as e:
        return f"Health check failed: {e}", 500


def run_server_forever():
    host = CFG.get("backend", {}).get("host", "0.0.0.0")
    port = CFG.get("backend", {}).get("port", 8080)

    # Main bulletproof loop
    while True:
        try:
            logger.info(f"[BACKEND] Starting GremlinGPT backend on {host}:{port}")
            broadcast_status(f"GremlinGPT backend server online at {host}:{port}")
            
            if socketio:
                socketio.run(app, host=host, port=port)
            else:
                # Fallback to regular Flask without SocketIO
                app.run(host=host, port=port, debug=False)
                
        except KeyboardInterrupt:
            logger.warning(
                "[BACKEND] KeyboardInterrupt received. Shutting down server."
            )
            broadcast_status("GremlinGPT backend server received shutdown signal.")
            break
        except Exception as e:
            import traceback
            err_info = f"[BACKEND] Server error: {e}\n{traceback.format_exc()}"
            logger.error(err_info)
            broadcast_status(
                f"GremlinGPT backend server encountered error and is restarting: {e}"
            )
            # Wait before restart to avoid busy-loop
            import time
            time.sleep(5)
        else:
            # If server exits cleanly, break loop
            broadcast_status("GremlinGPT backend server exited cleanly.")
            break

if __name__ == "__main__":
    run_server_forever()

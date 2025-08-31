#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: Module Integrity Directive

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
    print("[SERVER] SocketIO initialized")
else:
    socketio = None
    print("[SERVER] Running without SocketIO support")

from backend.globals import CFG, logger, resolve_path, DATA_DIR

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
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        logger.info(f"[CHAT] Received message: {message}")
        
        # Simple echo response for now - will be replaced with actual NLP processing
        response = f"Echo: {message}"
        
        # In the future, this will call the NLP engine:
        # response = nlp_engine.process_message(message)
        
        logger.info(f"[CHAT] Sending response: {response}")
        
        return jsonify({
            'response': response,
            'status': 'success',
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

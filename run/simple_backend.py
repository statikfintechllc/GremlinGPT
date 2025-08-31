#!/usr/bin/env python3

"""
Simple Backend Server for Agent Status API
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, jsonify
from backend.api.agent_status import agent_status_bp

app = Flask(__name__)

# Register the agent status blueprint
app.register_blueprint(agent_status_bp)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Backend API server running"})

@app.route('/')
def root():
    return jsonify({
        "service": "GremlinGPT Backend API",
        "endpoints": ["/health", "/api/agents/status"],
        "status": "online"
    })

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    print(f"Starting GremlinGPT Backend API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

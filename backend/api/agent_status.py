#!/usr/bin/env python3

# Agent Status API - Backend endpoint for checking agent status
# Provides agent connectivity information for frontend dashboard

from environments.dashboard import Flask, json, os, Path, logger, datetime
from flask import Blueprint, jsonify, request

# Try to import psutil if available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    psutil = None
    HAS_PSUTIL = False

# Create Flask Blueprint
agent_status_bp = Blueprint('agent_status', __name__)

def get_agent_status():
    """Get current status of all agents"""
    try:
        base_dir = Path(__file__).parent.parent.parent
        run_dir = base_dir / "run"
        
        # Agent status structure
        agents = {
            "planner": {"status": "offline", "pid": None, "uptime": 0},
            "data_analyst": {"status": "offline", "pid": None, "uptime": 0},
            "trading_strategist": {"status": "offline", "pid": None, "uptime": 0},
            "learning": {"status": "offline", "pid": None, "uptime": 0}
        }
        
        # Check agent coordinator status
        agent_coordinator_running = False
        agents_pid_file = run_dir / "agents.pid"
        
        if agents_pid_file.exists():
            try:
                with open(agents_pid_file, 'r') as f:
                    agent_pid = int(f.read().strip())
                
                if HAS_PSUTIL and psutil.pid_exists(agent_pid):
                    try:
                        proc = psutil.Process(agent_pid)
                        if proc.is_running():
                            agent_coordinator_running = True
                            # If agent coordinator is running, mark agents as active
                            for agent_name in agents:
                                agents[agent_name]["status"] = "active"
                                agents[agent_name]["pid"] = agent_pid
                                agents[agent_name]["uptime"] = proc.create_time()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except (ValueError, IOError):
                pass
        
        # Check orchestrator status
        orchestrator_running = False
        orchestrator_pid_file = run_dir / "orchestrator.pid"
        
        if orchestrator_pid_file.exists():
            try:
                with open(orchestrator_pid_file, 'r') as f:
                    orch_pid = int(f.read().strip())
                
                if HAS_PSUTIL and psutil.pid_exists(orch_pid):
                    try:
                        proc = psutil.Process(orch_pid)
                        orchestrator_running = proc.is_running()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except (ValueError, IOError):
                pass
        
        return {
            "agents": agents,
            "coordinator_running": agent_coordinator_running,
            "orchestrator_running": orchestrator_running,
            "timestamp": str(datetime.datetime.now())
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        return {
            "agents": {
                "planner": {"status": "error", "pid": None, "uptime": 0},
                "data_analyst": {"status": "error", "pid": None, "uptime": 0},
                "trading_strategist": {"status": "error", "pid": None, "uptime": 0},
                "learning": {"status": "error", "pid": None, "uptime": 0}
            },
            "coordinator_running": False,
            "orchestrator_running": False,
            "error": str(e)
        }

@agent_status_bp.route('/api/agent/status', methods=['GET'])
def api_agent_status():
    """Agent status API endpoint"""
    return jsonify(get_agent_status())

@agent_status_bp.route('/api/agents', methods=['GET'])
def api_agents_list():
    """List all agents"""
    status = get_agent_status()
    return jsonify({"agents": list(status["agents"].keys())})
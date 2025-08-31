#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT Agent Startup Script

import asyncio
import threading
import time
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from environments.orchestrator import logger, CFG

def start_agent_coordinator():
    """Start the main agent coordinator"""
    try:
        from agents.agent_coordinator import AgentCoordinator
        logger.info("[STARTUP] Initializing Agent Coordinator...")
        coordinator = AgentCoordinator()
        logger.info("[STARTUP] Agent Coordinator initialized successfully")
        
        # Keep the service running with a simple loop
        logger.info("[STARTUP] Starting agent service loop...")
        while True:
            try:
                # Check agent status every 30 seconds
                time.sleep(30)
                status = asyncio.run(coordinator.get_coordination_status())
                logger.info(f"[AGENTS] System status: {status.get('status', 'unknown')}")
            except KeyboardInterrupt:
                logger.info("[AGENTS] Shutdown signal received")
                break
            except Exception as e:
                logger.error(f"[AGENTS] Service loop error: {e}")
                time.sleep(10)  # Wait before retry
        
    except Exception as e:
        logger.error(f"[STARTUP] Agent Coordinator failed to start: {e}")
        import traceback
        logger.error(traceback.format_exc())

def start_individual_agents():
    """Start individual specialized agents"""
    agents = []
    
    # Start Data Analyst Agent
    try:
        from agents.data_analyst_agent import get_data_analyst_agent
        analyst = get_data_analyst_agent()
        agents.append(("DataAnalyst", analyst))
        logger.info("[STARTUP] Data Analyst Agent initialized")
    except Exception as e:
        logger.error(f"[STARTUP] Data Analyst Agent failed: {e}")
    
    # Start Trading Strategist Agent
    try:
        from agents.trading_strategist_agent import get_trading_strategist_agent
        trader = get_trading_strategist_agent()
        agents.append(("TradingStrategist", trader))
        logger.info("[STARTUP] Trading Strategist Agent initialized")
    except Exception as e:
        logger.error(f"[STARTUP] Trading Strategist Agent failed: {e}")
    
    # Start Learning Agent
    try:
        from agents.learning_agent import get_learning_agent
        learner = get_learning_agent()
        agents.append(("LearningAgent", learner))
        logger.info("[STARTUP] Learning Agent initialized")
    except Exception as e:
        logger.error(f"[STARTUP] Learning Agent failed: {e}")
    
    # Start Planner Agent background tasks
    try:
        from agents.planner_agent import inspect_task_queue, analyze_rewards
        logger.info("[STARTUP] Planner Agent background tasks ready")
        
        # Run periodic planner tasks
        def planner_loop():
            while True:
                try:
                    inspect_task_queue()
                    analyze_rewards()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"[PLANNER] Background task error: {e}")
                    time.sleep(10)
        
        planner_thread = threading.Thread(target=planner_loop, daemon=True)
        planner_thread.start()
        logger.info("[STARTUP] Planner Agent background loop started")
        
    except Exception as e:
        logger.error(f"[STARTUP] Planner Agent failed: {e}")
    
    return agents

def main():
    """Main startup sequence"""
    logger.info("[STARTUP] ===== GremlinGPT Agents Starting =====")
    
    # Create PID file
    pid_file = project_root / "run" / "agents.pid"
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    logger.info(f"[STARTUP] PID {os.getpid()} written to {pid_file}")
    
    try:
        # Start individual agents first
        agents = start_individual_agents()
        logger.info(f"[STARTUP] Started {len(agents)} individual agents")
        
        # Start the coordinator (this will run the main event loop)
        start_agent_coordinator()
        
    except KeyboardInterrupt:
        logger.info("[STARTUP] Received shutdown signal")
    except Exception as e:
        logger.error(f"[STARTUP] Critical error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Cleanup
        if pid_file.exists():
            pid_file.unlink()
        logger.info("[STARTUP] Agent system shutdown complete")

if __name__ == "__main__":
    main()

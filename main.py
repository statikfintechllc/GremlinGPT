#!/usr/bin/env python3

"""
GremlinGPT v1.0.3 - Main Entry Point
Autonomous, Self-Referential Cognitive System

This is the primary entry point for the GremlinGPT runtime.
Core components are initialized and managed from here.

Usage:
    python3 main.py              # Start full system
    python3 main.py --cli-only   # Start CLI interface only
    python3 main.py --status     # Check system status
"""

import sys
import os
import argparse
import logging
import asyncio
from pathlib import Path

# Set up base paths
BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BASE_DIR / 'data' / 'logs' / 'main.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


class GremlinGPT:
    """Main GremlinGPT system coordinator"""
    
    def __init__(self):
        self.base_dir = BASE_DIR
        self.data_dir = BASE_DIR / 'data'
        self.log_dir = self.data_dir / 'logs'
        self.components = {}
        self.backend_server = None
        self.backend_thread = None
        
        # Ensure directories exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def initialize_nlp(self):
        """Initialize custom NLP core (no external model dependencies)."""
        logger.info("Initializing NLP engine...")
        
        try:
            # Import with proper error handling
            from nlp_engine.nlp_core import NLPCore
            
            self.components['nlp'] = NLPCore()
            logger.info("✓ NLP engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize NLP engine: {e}")
            logger.error("System cannot run without functional NLP. Exiting.")
            return False
    
    def initialize_core(self):
        """Initialize core orchestrator and FSM"""
        logger.info("Initializing core orchestrator...")
        
        try:
            from core.orchestrator import initialize_orchestrator
            
            self.components['orchestrator'] = initialize_orchestrator()
            logger.info("✓ Core orchestrator initialized")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize orchestrator: {e}")
            return False
    
    def initialize_memory(self):
        """Initialize memory systems"""
        logger.info("Initializing memory systems...")
        
        try:
            from memory import log_history
            
            self.components['memory'] = log_history
            logger.info("✓ Memory systems initialized")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize memory: {e}")
            return False
    
    def initialize_agents(self):
        """Initialize agent coordinator"""
        logger.info("Initializing agents...")
        
        try:
            from agents.agent_coordinator import AgentCoordinator
            
            self.components['agents'] = AgentCoordinator()
            self._run_async(self.components['agents'].initialize_agents())
            logger.info("✓ Agents initialized")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize agents: {e}")
            return False

    def _run_async(self, coroutine):
        """Run async coroutine from sync code."""
        try:
            loop = asyncio.get_running_loop()
            future = asyncio.run_coroutine_threadsafe(coroutine, loop)
            return future.result()
        except RuntimeError:
            return asyncio.run(coroutine)

    def start_components(self):
        """Start managed components."""
        orchestrator = self.components.get('orchestrator')
        if orchestrator is not None and not getattr(orchestrator, 'running', False):
            self._run_async(orchestrator.start())
        return True

    def stop_components(self):
        """Stop managed components."""
        orchestrator = self.components.get('orchestrator')
        if orchestrator is not None and getattr(orchestrator, 'running', False):
            self._run_async(orchestrator.stop())

        agents = self.components.get('agents')
        if agents is not None and hasattr(agents, 'thread_pool'):
            agents.thread_pool.shutdown(wait=True)
        return True
    
    def start_cli(self):
        """Start CLI interface"""
        logger.info("Starting CLI interface...")
        
        print("\n" + "=" * 60)
        print("🌩️  GremlinGPT Terminal v1.0.3")
        print("=" * 60)
        print("Commands:")
        print("  start    - Start system components")
        print("  stop     - Stop system components")
        print("  status   - Show system status")
        print("  chat     - Chat with GremlinGPT")
        print("  help     - Show help")
        print("  exit     - Exit CLI")
        print("=" * 60 + "\n")
        
        while True:
            try:
                user_input = input("👤 > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ('exit', 'quit'):
                    logger.info("Exiting CLI...")
                    self.shutdown()
                    break
                
                # Parse command using NLP
                if 'nlp' in self.components:
                    parsed = self.components['nlp'].parse_command(user_input)
                    intent = parsed.get('intent', 'unknown')
                    
                    if intent == 'help':
                        print("\n🤖 GremlinGPT Help:")
                        print("  Commands: start, stop, status, chat, help, exit")
                        print()
                    elif intent == 'status':
                        self.show_status()
                    elif intent == 'start':
                        self.start_components()
                        print("🤖 System components started.")
                    elif intent == 'stop':
                        self.stop_components()
                        print("🤖 System components stopped.")
                    else:
                        # Treat as chat message
                        print(f"🤖 GremlinGPT: Processing: {user_input}")
                        # TODO: Implement chat handler
                else:
                    print("🤖 NLP not initialized. Please restart system.")
                    
            except KeyboardInterrupt:
                print("\n\nKeyboard interrupt detected. Exiting...")
                self.shutdown()
                break
            except EOFError:
                print("\n\nEOF detected. Exiting...")
                self.shutdown()
                break
            except Exception as e:
                logger.error(f"Error in CLI: {e}")
                print(f"Error: {e}")
    
    def start_backend(self):
        """Start backend API server"""
        logger.info("Starting backend API server...")
        
        try:
            import threading
            from werkzeug.serving import make_server
            from backend.server import app
            
            self.backend_server = make_server('127.0.0.1', 8080, app)
            self.backend_thread = threading.Thread(target=self.backend_server.serve_forever, daemon=True)
            self.backend_thread.start()
            logger.info("✓ Backend server started on port 8080")
            
        except Exception as e:
            logger.error(f"✗ Failed to start backend: {e}")
            raise

    def stop_backend(self):
        """Stop backend API server."""
        if self.backend_server is not None:
            self.backend_server.shutdown()
            self.backend_server = None
        if self.backend_thread is not None:
            self.backend_thread.join(timeout=5)
            self.backend_thread = None

    def shutdown(self):
        """Gracefully shut down all initialized components."""
        self.stop_backend()
        self.stop_components()
    
    def run_full_system(self):
        """Start all system components"""
        logger.info("=" * 60)
        logger.info("GremlinGPT v1.0.3 - Starting Full System")
        logger.info("=" * 60)
        
        # Initialize components in order
        if not self.initialize_nlp():
            sys.exit(1)
        
        if not self.initialize_core():
            sys.exit(1)
        
        if not self.initialize_memory():
            sys.exit(1)
        
        if not self.initialize_agents():
            sys.exit(1)
        
        # Start managed runtime components and services
        self.start_components()
        self.start_backend()
        
        logger.info("=" * 60)
        logger.info("✓ All systems initialized successfully")
        logger.info("Backend API: http://localhost:8080")
        logger.info("=" * 60)
        
        # Start CLI as main interface
        self.start_cli()
    
    def show_status(self):
        """Show system status"""
        logger.info("=" * 60)
        logger.info("GremlinGPT System Status")
        logger.info("=" * 60)
        
        # Check if components are running
        status = {
            'NLP Engine': 'Ready' if 'nlp' in self.components else 'Not initialized',
            'Core Orchestrator': 'Running' if getattr(self.components.get('orchestrator'), 'running', False) else ('Ready' if 'orchestrator' in self.components else 'Not initialized'),
            'Memory Systems': 'Ready' if 'memory' in self.components else 'Not initialized',
            'Agents': 'Ready' if getattr(self.components.get('agents'), 'agents', None) else ('Not initialized' if 'agents' not in self.components else 'Degraded'),
            'Backend API': 'Running' if self.backend_thread is not None and self.backend_thread.is_alive() else 'Stopped'
        }
        
        # Try to ping each component
        for component, state in status.items():
            logger.info(f"{component}: {state}")
        
        logger.info("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='GremlinGPT - Autonomous Cognitive System'
    )
    parser.add_argument(
        '--cli-only',
        action='store_true',
        help='Start CLI interface only'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Check system status'
    )
    
    args = parser.parse_args()
    
    # Create system instance
    system = GremlinGPT()
    
    if args.status:
        system.show_status()
    elif args.cli_only:
        if system.initialize_nlp():
            system.start_cli()
    else:
        system.run_full_system()


if __name__ == '__main__':
    main()

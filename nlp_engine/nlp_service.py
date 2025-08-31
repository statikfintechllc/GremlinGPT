#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: NLP Service Main Entry Point
# Unified NLP Engine Service - coordinates all NLP components as one system

# Import NLP environment globals
from conda_envs.environments.nlp.globals import *

import sys
import os
import json
import traceback
from datetime import datetime
from flask import Flask, request, jsonify
import threading
import time

# Import all NLP components
try:
    from .tokenizer import Tokenizer, tokenize
    from .transformer_core import TransformerCore, encode
    from .mini_attention import MiniMultiHeadAttention
    from .chat_session import ChatSession
    from .parser import parse_nlp
    from .semantic_score import reasoned_similarity
    from .pos_tagger import get_pos_tags
    from .diff_engine import diff_texts
except ImportError as e:
    logger.warning(f"Some NLP components not available for relative import: {e}")
    # Try absolute imports as fallback
    try:
        from nlp_engine.tokenizer import Tokenizer, tokenize
        from nlp_engine.transformer_core import TransformerCore, encode
        from nlp_engine.mini_attention import MiniMultiHeadAttention
        from nlp_engine.chat_session import ChatSession
        from nlp_engine.semantic_score import reasoned_similarity
        from nlp_engine.parser import parse_nlp
        from nlp_engine.pos_tagger import get_pos_tags
        from nlp_engine.diff_engine import diff_texts
    except ImportError as e2:
        logger.error(f"Critical: Could not import NLP components: {e2}")
        # Create fallback functions to prevent total failure
        logger.warning("Creating fallback NLP components to ensure service can start")
        
        class Tokenizer:
            def tokenize(self, text): 
                return text.split()
        
        class TransformerCore:
            def __init__(self):
                self.device = "cpu"
            def process(self, tokens): 
                return tokens
            def forward(self, tokens):
                if isinstance(tokens, list):
                    return " ".join(tokens)
                return str(tokens)
        
        class MiniMultiHeadAttention:
            def __init__(self, embed_dim=384, num_heads=8, scale=True, seed=42):
                self.embed_dim = embed_dim
                self.num_heads = num_heads
            def forward(self, input_tensor):
                # Return dummy output with same shape
                import numpy as np
                output = np.zeros_like(input_tensor)
                weights = np.zeros((self.num_heads, input_tensor.shape[0], input_tensor.shape[0]))
                return output, weights
        
        class ChatSession:
            def __init__(self, user_id="anonymous"):
                self.session_id = f"fallback_{user_id}"
            def process_input(self, text):
                return {"response": f"Fallback response to: {text}", "session_id": self.session_id}
        
        def tokenize(text):
            return text.split()
        
        def encode(text):
            import numpy as np
            return np.zeros(384, dtype=np.float32)
        
        def parse_nlp(text): 
            return {"route": "general", "tokens": text.split(), "pos": [], "entities": [], "dependencies": [], "code_entities": [], "financial_hits": []}
        
        def get_pos_tags(text): 
            return []
        
        def diff_texts(text1, text2): 
            return {"diff_lines": [], "semantic_score": 0.0, "embedding_delta": 0.0}
        
        def reasoned_similarity(text1, text2):
            return {"similarity": 0.0, "explanation": "fallback mode"}

# For cross-environment communication, use lazy loading
def lazy_import_memory():
    """Lazy import memory functionality to prevent circular dependencies"""
    try:
        from memory.vector_store.embedder import embed_text, package_embedding
        from memory.log_history import log_event
        return embed_text, package_embedding, log_event
    except ImportError as e:
        logger.warning(f"Memory functions not available: {e}")
        return None, None, None

def lazy_import_orchestrator():
    """Lazy import orchestrator functionality to prevent circular dependencies"""
    try:
        from agent_core.fsm import inject_task
        return inject_task
    except ImportError as e:
        logger.warning(f"Orchestrator functions not available: {e}")
        return None

# Get cross-environment functions lazily
embed_text, package_embedding, log_event = lazy_import_memory()
inject_task = lazy_import_orchestrator()

class NLPService:
    """
    Unified NLP Service that coordinates all NLP components as one system.
    Provides REST API endpoints for other services to interact with.
    """
    
    def __init__(self, port=8001):
        self.port = port
        self.app = Flask(__name__)
        self.app.config['JSON_SORT_KEYS'] = False
        
        # Initialize NLP components
        logger.info("[NLP_SERVICE] Initializing NLP components...")
        
        # Core components
        self.tokenizer = Tokenizer()
        self.transformer = TransformerCore()
        self.attention = MiniMultiHeadAttention(embed_dim=384, num_heads=8, scale=True, seed=42)
        
        # Session management
        self.chat_sessions = {}
        
        # Service status
        self.start_time = datetime.now()
        self.request_count = 0
        self.health_status = "initializing"
        
        # Setup routes
        self._setup_routes()
        
        # Run health check
        self._perform_health_check()
        
        logger.success("[NLP_SERVICE] NLP Service initialized successfully")
    
    def _setup_routes(self):
        """Setup Flask API routes for NLP service"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": self.health_status,
                "uptime": str(datetime.now() - self.start_time),
                "request_count": self.request_count,
                "components": {
                    "tokenizer": "available" if self.tokenizer else "unavailable",
                    "transformer": "available" if self.transformer else "unavailable",
                    "attention": "available" if self.attention else "unavailable"
                },
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/tokenize', methods=['POST'])
        def tokenize_text():
            """Tokenize input text"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get('text', '')
                
                if not text:
                    return jsonify({"error": "No text provided"}), 400
                
                tokens = tokenize(text)
                
                return jsonify({
                    "tokens": tokens,
                    "count": len(tokens),
                    "original_text": text
                })
                
            except Exception as e:
                logger.error(f"[NLP_SERVICE] Tokenization error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/encode', methods=['POST'])
        def encode_text():
            """Encode text to vector using transformer"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get('text', '')
                
                if not text:
                    return jsonify({"error": "No text provided"}), 400
                
                vector = encode(text)
                
                return jsonify({
                    "vector": vector.tolist(),
                    "dimension": len(vector),
                    "original_text": text
                })
                
            except Exception as e:
                logger.error(f"[NLP_SERVICE] Encoding error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/chat', methods=['POST'])
        def chat_endpoint():
            """Chat interface using NLP pipeline"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get('text', '')
                user_id = data.get('user_id', 'anonymous')
                session_id = data.get('session_id', None)
                
                if not text:
                    return jsonify({"error": "No text provided"}), 400
                
                # Get or create chat session
                if session_id and session_id in self.chat_sessions:
                    session = self.chat_sessions[session_id]
                else:
                    session = ChatSession(user_id=user_id)
                    self.chat_sessions[session.session_id] = session
                
                # Process input through chat session
                response = session.process_input(text)
                
                return jsonify({
                    "response": response["response"],
                    "session_id": response["session_id"],
                    "user_id": user_id
                })
                
            except Exception as e:
                logger.error(f"[NLP_SERVICE] Chat error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/similarity', methods=['POST'])
        def similarity_check():
            """Check semantic similarity between two texts"""
            self.request_count += 1
            try:
                data = request.get_json()
                text1 = data.get('text1', '')
                text2 = data.get('text2', '')
                
                if not text1 or not text2:
                    return jsonify({"error": "Both text1 and text2 required"}), 400
                
                similarity = reasoned_similarity(text1, text2)
                
                return jsonify({
                    "similarity": similarity,
                    "text1": text1,
                    "text2": text2
                })
                
            except Exception as e:
                logger.error(f"[NLP_SERVICE] Similarity error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/parse', methods=['POST'])
        def parse_endpoint():
            """Parse text structure"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get('text', '')
                
                if not text:
                    return jsonify({"error": "No text provided"}), 400
                
                parsed = parse_nlp(text)
                
                return jsonify({
                    "parsed": parsed,
                    "original_text": text
                })
                
            except Exception as e:
                logger.error(f"[NLP_SERVICE] Parsing error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/pos_tag', methods=['POST'])
        def pos_tag_endpoint():
            """Part-of-speech tagging"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get('text', '')
                
                if not text:
                    return jsonify({"error": "No text provided"}), 400
                
                tags = get_pos_tags(text)
                
                return jsonify({
                    "tags": tags,
                    "original_text": text
                })
                
            except Exception as e:
                logger.error(f"[NLP_SERVICE] POS tagging error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/diff', methods=['POST'])
        def diff_endpoint():
            """Compare two texts and show differences"""
            self.request_count += 1
            try:
                data = request.get_json()
                text1 = data.get('text1', '')
                text2 = data.get('text2', '')
                
                if not text1 or not text2:
                    return jsonify({"error": "Both text1 and text2 required"}), 400
                
                diff = diff_texts(text1, text2)
                
                return jsonify({
                    "diff": diff,
                    "text1": text1,
                    "text2": text2
                })
                
            except Exception as e:
                logger.error(f"[NLP_SERVICE] Diff error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/attention', methods=['POST'])
        def attention_endpoint():
            """Process text through attention mechanism"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get('text', '')
                
                if not text:
                    return jsonify({"error": "No text provided"}), 400
                
                # Encode text to vector
                vector = encode(text)
                
                # Reshape for attention (assuming single sequence)
                input_tensor = vector.reshape(1, -1)  # (1, embed_dim)
                
                # Apply attention
                output, weights = self.attention.forward(input_tensor)
                
                return jsonify({
                    "output": output.tolist(),
                    "attention_weights": weights.tolist(),
                    "input_shape": input_tensor.shape,
                    "output_shape": output.shape,
                    "original_text": text
                })
                
            except Exception as e:
                logger.error(f"[NLP_SERVICE] Attention error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/status', methods=['GET'])
        def status_endpoint():
            """Detailed service status"""
            return jsonify({
                "service": "NLP Engine",
                "status": self.health_status,
                "port": self.port,
                "uptime": str(datetime.now() - self.start_time),
                "requests_served": self.request_count,
                "active_sessions": len(self.chat_sessions),
                "components": {
                    "tokenizer": {
                        "status": "available" if self.tokenizer else "unavailable",
                        "type": type(self.tokenizer).__name__ if self.tokenizer else None
                    },
                    "transformer": {
                        "status": "available" if self.transformer else "unavailable", 
                        "device": getattr(self.transformer, 'device', 'unknown') if self.transformer else None
                    },
                    "attention": {
                        "status": "available" if self.attention else "unavailable",
                        "heads": getattr(self.attention, 'num_heads', 'unknown') if self.attention else None,
                        "embed_dim": getattr(self.attention, 'embed_dim', 'unknown') if self.attention else None
                    }
                },
                "endpoints": [
                    "/health", "/tokenize", "/encode", "/chat", 
                    "/similarity", "/parse", "/pos_tag", "/diff", "/attention", "/status", "/api"
                ],
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api', methods=['GET'])
        def api_documentation():
            """API documentation endpoint"""
            return jsonify({
                "service": "GremlinGPT NLP Engine API",
                "version": "1.0.3",
                "description": "Unified NLP service providing tokenization, encoding, chat, parsing, and analysis capabilities",
                "base_url": f"http://localhost:{self.port}",
                "endpoints": {
                    "/health": {
                        "method": "GET",
                        "description": "Service health check",
                        "response": "Service status, uptime, and component availability"
                    },
                    "/status": {
                        "method": "GET", 
                        "description": "Detailed service status",
                        "response": "Comprehensive service information"
                    },
                    "/tokenize": {
                        "method": "POST",
                        "description": "Tokenize input text",
                        "body": {"text": "string"},
                        "response": {"tokens": ["array"], "count": "number", "original_text": "string"}
                    },
                    "/encode": {
                        "method": "POST",
                        "description": "Encode text to vector representation",
                        "body": {"text": "string"},
                        "response": {"vector": ["array"], "dimension": "number", "original_text": "string"}
                    },
                    "/chat": {
                        "method": "POST",
                        "description": "Chat interface with session management",
                        "body": {"text": "string", "user_id": "string (optional)", "session_id": "string (optional)"},
                        "response": {"response": "string", "session_id": "string", "user_id": "string"}
                    },
                    "/similarity": {
                        "method": "POST",
                        "description": "Calculate semantic similarity between two texts",
                        "body": {"text1": "string", "text2": "string"},
                        "response": {"similarity": "object", "text1": "string", "text2": "string"}
                    },
                    "/parse": {
                        "method": "POST",
                        "description": "Parse text structure and extract linguistic features",
                        "body": {"text": "string"},
                        "response": {"parsed": "object", "original_text": "string"}
                    },
                    "/pos_tag": {
                        "method": "POST",
                        "description": "Part-of-speech tagging",
                        "body": {"text": "string"},
                        "response": {"tags": ["array"], "original_text": "string"}
                    },
                    "/diff": {
                        "method": "POST",
                        "description": "Compare two texts and show differences",
                        "body": {"text1": "string", "text2": "string"},
                        "response": {"diff": "object", "text1": "string", "text2": "string"}
                    },
                    "/attention": {
                        "method": "POST",
                        "description": "Process text through attention mechanism",
                        "body": {"text": "string"},
                        "response": {"output": ["array"], "attention_weights": ["array"], "input_shape": ["array"], "output_shape": ["array"], "original_text": "string"}
                    }
                },
                "examples": {
                    "tokenize": "curl -X POST -H 'Content-Type: application/json' -d '{\"text\":\"Hello world\"}' http://localhost:8001/tokenize",
                    "encode": "curl -X POST -H 'Content-Type: application/json' -d '{\"text\":\"Hello world\"}' http://localhost:8001/encode",
                    "chat": "curl -X POST -H 'Content-Type: application/json' -d '{\"text\":\"What is trading?\",\"user_id\":\"trader1\"}' http://localhost:8001/chat"
                }
            })
    
    def _perform_health_check(self):
        """Perform internal health check of all components"""
        try:
            # Test tokenizer
            test_tokens = tokenize("Health check test")
            assert len(test_tokens) > 0, "Tokenizer failed"
            
            # Test transformer
            test_vector = encode("Health check test")
            assert test_vector is not None and len(test_vector) > 0, "Transformer failed"
            
            # Test attention
            input_tensor = test_vector.reshape(1, -1)
            output, weights = self.attention.forward(input_tensor)
            assert output is not None, "Attention failed"
            
            self.health_status = "healthy"
            logger.success("[NLP_SERVICE] Health check passed - all components operational")
            
            # Log to system if available
            if log_event:
                log_event("nlp_service", "health_check", {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "components_tested": ["tokenizer", "transformer", "attention"]
                })
            
        except Exception as e:
            self.health_status = "degraded"
            logger.error(f"[NLP_SERVICE] Health check failed: {e}")
            
            # Log to system if available
            if log_event:
                log_event("nlp_service", "health_check", {
                    "status": "degraded",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def run(self, debug=False, threaded=True):
        """Run the NLP service"""
        logger.info(f"[NLP_SERVICE] Starting NLP Service on port {self.port}")
        logger.info(f"[NLP_SERVICE] Service endpoints available at http://localhost:{self.port}")
        
        try:
            self.app.run(
                host='0.0.0.0',
                port=self.port,
                debug=debug,
                threaded=threaded,
                use_reloader=False  # Disable reloader to prevent issues in production
            )
        except Exception as e:
            logger.error(f"[NLP_SERVICE] Failed to start service: {e}")
            self.health_status = "failed"
            raise

def main():
    """Main entry point for NLP Service"""
    # Get port from environment or command line
    port = int(os.environ.get('NLP_PORT', 8001))
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.warning(f"Invalid port argument: {sys.argv[1]}, using default {port}")
    
    # Create and run service
    service = NLPService(port=port)
    
    try:
        service.run(debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("[NLP_SERVICE] Service stopped by user")
    except Exception as e:
        logger.error(f"[NLP_SERVICE] Service failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
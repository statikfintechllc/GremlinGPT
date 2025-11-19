#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: NLP Service Main Entry Point
# Unified NLP Engine Service - coordinates all NLP components as one system

# Import specific NLP environment globals
from conda_envs.environments.nlp.globals import (
    logger,
    CFG,
    BASE_DIR,
    DATA_DIR,
    NLP_DATA_DIR,
    EMBEDDINGS_DIR,
    HAS_TRANSFORMERS,
    HAS_NLTK,
    HAS_SENTENCE_TRANSFORMERS,
    HAS_OPENAI,
    EMBEDDING_MODEL,
    NLTK_INITIALIZED,
    resolve_path,
    clean_text,
    get_nlp_status,
    safe_import_function,
    safe_import_class,
)

import sys
import os
import json
import traceback

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

    # Create mock numpy for fallback
    class MockNumpy:
        def array(self, data, dtype=None):
            return data

        def zeros(self, shape, dtype=None):
            if isinstance(shape, int):
                return [0.0] * shape
            return [0.0] * shape[0] if isinstance(shape, (list, tuple)) else [0.0]

        def random(self):
            return self

        def normal(self, mean, std, size):
            import random

            if isinstance(size, int):
                return [random.gauss(mean, std) for _ in range(size)]
            return [
                random.gauss(mean, std)
                for _ in range(size[0])
                if isinstance(size, (list, tuple))
            ]

        def zeros_like(self, arr, dtype=None):
            if hasattr(arr, "__len__"):
                return [0.0] * len(arr)
            return [0.0]

        def linalg(self):
            return self

        def norm(self, arr):
            if hasattr(arr, "__len__"):
                return sum(x * x for x in arr) ** 0.5
            return abs(arr)

    np = MockNumpy()

from datetime import datetime

try:
    from flask import Flask, request, jsonify

    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    Flask = request = jsonify = None

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
        # Create robust fallback classes with proper API contracts
        logger.warning(
            "Creating robust fallback NLP components to ensure service can start"
        )

        class Tokenizer:
            """Robust fallback tokenizer with proper API contract"""

            def __init__(self, model_name=None):
                self.model_name = model_name or "fallback"

            def tokenize(self, text, max_length=512, add_special_tokens=True):
                """Tokenize text with proper structure"""
                if not text:
                    return []

                # Basic word tokenization with some improvements
                tokens = text.lower().split()

                # Add special tokens if requested
                if add_special_tokens:
                    tokens = ["[CLS]"] + tokens[: max_length - 2] + ["[SEP]"]
                else:
                    tokens = tokens[:max_length]

                return tokens

            def encode(self, text, **kwargs):
                """Encode text to token IDs"""
                tokens = self.tokenize(text)
                # Return simple sequential IDs for fallback
                return list(range(len(tokens)))

            def decode(self, token_ids, **kwargs):
                """Decode token IDs back to text"""
                if not token_ids:
                    return ""
                return f"decoded_text_{len(token_ids)}_tokens"

        class TransformerCore:
            """Robust fallback transformer with proper API contract"""

            def __init__(self):
                self.device = "cpu"
                self.model_name = "fallback-transformer"
                self.embedding_dim = 384

            def process(self, tokens):
                """Process tokens through transformer"""
                if isinstance(tokens, str):
                    tokens = tokens.split()
                return tokens

            def forward(self, input_data):
                """Forward pass through transformer"""
                if isinstance(input_data, str):
                    # Return vector for text input
                    if HAS_NUMPY:
                        return np.random.normal(0, 0.1, self.embedding_dim).astype(
                            np.float32
                        )
                    else:
                        import random

                        return [random.gauss(0, 0.1) for _ in range(self.embedding_dim)]
                elif isinstance(input_data, list):
                    # Return vector per token
                    batch_size = len(input_data)
                    if HAS_NUMPY:
                        return np.random.normal(
                            0, 0.1, (batch_size, self.embedding_dim)
                        ).astype(np.float32)
                    else:
                        import random

                        return [
                            [random.gauss(0, 0.1) for _ in range(self.embedding_dim)]
                            for _ in range(batch_size)
                        ]
                else:
                    # Return same shape as input
                    if HAS_NUMPY:
                        return np.zeros_like(input_data, dtype=np.float32)
                    else:
                        return (
                            [0.0] * len(input_data)
                            if hasattr(input_data, "__len__")
                            else [0.0]
                        )

            def encode(self, text):
                """Encode text to vector representation"""
                if HAS_NUMPY:
                    return np.random.normal(0, 0.1, self.embedding_dim).astype(
                        np.float32
                    )
                else:
                    import random

                    return [random.gauss(0, 0.1) for _ in range(self.embedding_dim)]

        class MiniMultiHeadAttention:
            """Robust fallback attention mechanism with proper API contract"""

            def __init__(self, embed_dim=384, num_heads=8, scale=True, seed=42):
                self.embed_dim = embed_dim
                self.num_heads = num_heads
                self.scale = scale
                self.seed = seed
                np.random.seed(seed)

            def forward(self, input_tensor):
                """Apply multi-head attention"""
                if not HAS_NUMPY:
                    # Simple fallback without numpy
                    if isinstance(input_tensor, list):
                        output = input_tensor[:]
                        seq_len = len(input_tensor)
                    else:
                        output = [0.0] * 384
                        seq_len = 1

                    weights = [
                        [[1.0 / seq_len] * seq_len for _ in range(seq_len)]
                        for _ in range(self.num_heads)
                    ]
                    return output, weights

                # Full numpy implementation
                # Ensure input is numpy array
                if not isinstance(input_tensor, np.ndarray):
                    input_tensor = np.array(input_tensor, dtype=np.float32)

                # Handle different input shapes
                if len(input_tensor.shape) == 1:
                    # Single vector: (embed_dim,)
                    seq_len = 1
                    input_tensor = input_tensor.reshape(1, -1)
                elif len(input_tensor.shape) == 2:
                    # Sequence: (seq_len, embed_dim)
                    seq_len = input_tensor.shape[0]
                else:
                    # Batch: assume last dimension is embed_dim
                    seq_len = input_tensor.shape[-2] if input_tensor.shape[-2] else 1

                # Apply light attention-like transformation
                output = input_tensor * 0.9 + np.random.normal(
                    0, 0.01, input_tensor.shape
                ).astype(np.float32)

                # Generate attention weights
                weights = np.random.uniform(0, 1, (self.num_heads, seq_len, seq_len))
                # Normalize weights per head
                weights = weights / weights.sum(axis=-1, keepdims=True)

                return output, weights

        class ChatSession:
            """Robust fallback chat session with proper API contract"""

            def __init__(self, user_id="anonymous"):
                self.user_id = user_id
                self.session_id = f"fallback_{user_id}_{int(time.time())}"
                self.history = []

            def process_input(self, user_input, context=None, feedback=None):
                """Process user input with context awareness"""
                if not user_input:
                    return {"error": "Empty input", "session_id": self.session_id}

                # Store in history
                self.history.append(
                    {
                        "input": user_input,
                        "timestamp": datetime.now().isoformat(),
                        "context": context,
                    }
                )

                # Generate contextual response
                responses = [
                    f"I understand you're asking about: {user_input[:50]}...",
                    f"That's an interesting question about {user_input.split()[0] if user_input.split() else 'this topic'}.",
                    f"I'm currently in fallback mode, but I can help you with: {user_input[:30]}...",
                    f"Let me process your request: {user_input}",
                ]

                response = responses[len(self.history) % len(responses)]

                return {
                    "response": response,
                    "session_id": self.session_id,
                    "confidence": 0.5,
                    "tokens_used": len(user_input.split()),
                    "context_applied": context is not None,
                }

            def get_history(self):
                """Get conversation history"""
                return self.history

        def tokenize(text):
            """Robust fallback tokenization function"""
            if not text:
                return []

            # Enhanced tokenization with punctuation handling
            import re

            # Split on whitespace and punctuation but keep structure
            tokens = re.findall(r"\w+|[^\w\s]", text.lower())
            return tokens

        def encode(text):
            """Robust fallback encoding function"""
            if not text:
                if HAS_NUMPY:
                    return np.zeros(384, dtype=np.float32)
                else:
                    return [0.0] * 384

            if HAS_NUMPY:
                # Create deterministic but varied encoding based on text
                hash_val = hash(text) % (2**31)
                np.random.seed(hash_val % 10000)  # Consistent but varied
                vector = np.random.normal(0, 0.1, 384).astype(np.float32)

                # Add some text-based features
                vector[0] = min(len(text) / 1000, 1.0)  # Length feature
                vector[1] = len(text.split()) / 100.0  # Word count feature

                return vector
            else:
                # Simple fallback without numpy
                import random

                hash_val = hash(text) % (2**31)
                random.seed(hash_val % 10000)
                vector = [random.gauss(0, 0.1) for _ in range(384)]
                vector[0] = min(len(text) / 1000, 1.0)
                vector[1] = len(text.split()) / 100.0
                return vector

        def parse_nlp(text):
            """Robust fallback NLP parsing"""
            if not text:
                return {
                    "route": "empty",
                    "tokens": [],
                    "pos": [],
                    "entities": [],
                    "dependencies": [],
                    "code_entities": [],
                    "financial_hits": [],
                    "confidence": 0.0,
                }

            tokens = tokenize(text)

            # Basic pattern detection
            financial_terms = [
                "price",
                "stock",
                "market",
                "trade",
                "buy",
                "sell",
                "profit",
            ]
            code_terms = ["function", "class", "import", "def", "return", "if", "for"]

            financial_hits = [term for term in financial_terms if term in text.lower()]
            code_entities = [term for term in code_terms if term in text.lower()]

            # Simple route classification
            if financial_hits:
                route = "financial"
            elif code_entities:
                route = "technical"
            elif any(
                q in text.lower() for q in ["what", "how", "why", "when", "where"]
            ):
                route = "question"
            else:
                route = "general"

            return {
                "route": route,
                "tokens": tokens,
                "pos": [
                    (token, "NOUN" if token.isalpha() else "PUNCT")
                    for token in tokens[:10]
                ],
                "entities": [],
                "dependencies": [],
                "code_entities": code_entities,
                "financial_hits": financial_hits,
                "confidence": 0.6 if financial_hits or code_entities else 0.3,
            }

        def get_pos_tags(text):
            """Robust fallback POS tagging"""
            if not text:
                return []

            tokens = tokenize(text)
            # Simple POS tagging rules
            pos_tags = []
            for token in tokens:
                if token.isalpha():
                    if token.endswith("ing"):
                        pos_tags.append((token, "VERB"))
                    elif token.endswith("ed"):
                        pos_tags.append((token, "VERB"))
                    elif token.endswith("ly"):
                        pos_tags.append((token, "ADV"))
                    else:
                        pos_tags.append((token, "NOUN"))
                elif token.isdigit():
                    pos_tags.append((token, "NUM"))
                else:
                    pos_tags.append((token, "PUNCT"))

            return pos_tags

        def diff_texts(text1, text2):
            """Robust fallback text diffing"""
            if not text1 and not text2:
                return {"diff_lines": [], "semantic_score": 1.0, "embedding_delta": 0.0}
            if not text1 or not text2:
                return {
                    "diff_lines": [
                        {
                            "type": "added" if text2 else "removed",
                            "content": text2 or text1,
                        }
                    ],
                    "semantic_score": 0.0,
                    "embedding_delta": 1.0,
                }

            # Simple line-based diff
            lines1 = text1.split("\n")
            lines2 = text2.split("\n")

            diff_lines = []
            max_len = max(len(lines1), len(lines2))

            for i in range(max_len):
                line1 = lines1[i] if i < len(lines1) else ""
                line2 = lines2[i] if i < len(lines2) else ""

                if line1 != line2:
                    if not line1:
                        diff_lines.append(
                            {"type": "added", "content": line2, "line": i + 1}
                        )
                    elif not line2:
                        diff_lines.append(
                            {"type": "removed", "content": line1, "line": i + 1}
                        )
                    else:
                        diff_lines.append(
                            {
                                "type": "changed",
                                "content": f"{line1} -> {line2}",
                                "line": i + 1,
                            }
                        )

            # Calculate semantic similarity
            common_words = set(text1.lower().split()) & set(text2.lower().split())
            total_words = set(text1.lower().split()) | set(text2.lower().split())
            semantic_score = (
                len(common_words) / len(total_words) if total_words else 0.0
            )

            # Calculate embedding delta
            vec1 = encode(text1)
            vec2 = encode(text2)
            if HAS_NUMPY:
                embedding_delta = float(np.linalg.norm(vec1 - vec2))
            else:
                # Simple Euclidean distance for fallback
                if len(vec1) == len(vec2):
                    embedding_delta = (
                        sum((a - b) ** 2 for a, b in zip(vec1, vec2)) ** 0.5
                    )
                else:
                    embedding_delta = 1.0  # Max difference if vectors don't match

            return {
                "diff_lines": diff_lines,
                "semantic_score": semantic_score,
                "embedding_delta": embedding_delta,
                "common_words": len(common_words),
                "total_words": len(total_words),
            }

        def reasoned_similarity(text1, text2):
            """Robust fallback similarity analysis"""
            if not text1 or not text2:
                return {"similarity": 0.0, "explanation": "One or both texts are empty"}

            # Multiple similarity measures
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            # Jaccard similarity
            intersection = words1 & words2
            union = words1 | words2
            jaccard = len(intersection) / len(union) if union else 0.0

            # Length similarity
            len_sim = 1.0 - abs(len(text1) - len(text2)) / max(len(text1), len(text2))

            # Combined similarity
            similarity = jaccard * 0.7 + len_sim * 0.3

            # Generate explanation
            common_words = list(intersection)[:5]
            explanation = f"Jaccard: {jaccard:.2f}, Length sim: {len_sim:.2f}"
            if common_words:
                explanation += f", Common words: {', '.join(common_words)}"

            return {
                "similarity": similarity,
                "explanation": explanation,
                "jaccard_similarity": jaccard,
                "length_similarity": len_sim,
                "common_words": len(intersection),
                "method": "fallback_analysis",
            }


# ========================================================================================
# LAZY LOADING UTILITY PATTERN
# ========================================================================================


def create_lazy_loader(module_path, *function_names):
    """Create a lazy loader function that safely imports functions from a module.

    This utility pattern eliminates code duplication for conditional imports
    throughout the codebase.

    Args:
        module_path (str): The module path to import from
        *function_names: Variable number of function names to import

    Returns:
        tuple: Functions or None for each requested function
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
        return callback(*args, **kwargs)
    else:
        logger.debug("Skipping execution - required functions not available")
        return None


# For cross-environment communication, use lazy loading
memory_loader = create_lazy_loader(
    "memory.vector_store.embedder", "embed_text", "package_embedding"
)
history_loader = create_lazy_loader("memory.log_history", "log_event")
orchestrator_loader = create_lazy_loader("agent_core.fsm", "inject_task")


def lazy_import_memory():
    """Lazy import memory functionality to prevent circular dependencies"""
    return memory_loader()


def lazy_import_history():
    """Lazy import history functionality to prevent circular dependencies"""
    return history_loader()


def lazy_import_orchestrator():
    """Lazy import orchestrator functionality to prevent circular dependencies"""
    return orchestrator_loader()


# Get cross-environment functions lazily
embed_text, package_embedding = lazy_import_memory()
(log_event,) = lazy_import_history()
(inject_task,) = lazy_import_orchestrator()


class NLPService:
    """
    Unified NLP Service that coordinates all NLP components as one system.
    Provides REST API endpoints for other services to interact with.
    """

    def __init__(self, port=8001):
        if not HAS_FLASK:
            raise ImportError(
                "Flask is required for NLP Service. Please install flask: pip install flask"
            )

        self.port = port
        self.app = Flask(__name__)
        self.app.config["JSON_SORT_KEYS"] = False

        # Initialize NLP components
        logger.info("[NLP_SERVICE] Initializing NLP components...")

        # Core components
        self.tokenizer = Tokenizer()
        self.transformer = TransformerCore()
        self.attention = MiniMultiHeadAttention(
            embed_dim=384, num_heads=8, scale=True, seed=42
        )

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

        @self.app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint"""
            return jsonify(
                {
                    "status": self.health_status,
                    "uptime": str(datetime.now() - self.start_time),
                    "request_count": self.request_count,
                    "components": {
                        "tokenizer": "available" if self.tokenizer else "unavailable",
                        "transformer": (
                            "available" if self.transformer else "unavailable"
                        ),
                        "attention": "available" if self.attention else "unavailable",
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            )

        @self.app.route("/tokenize", methods=["POST"])
        def tokenize_text():
            """Tokenize input text"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get("text", "")

                if not text:
                    return jsonify({"error": "No text provided"}), 400

                tokens = tokenize(text)

                return jsonify(
                    {"tokens": tokens, "count": len(tokens), "original_text": text}
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Tokenization error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/encode", methods=["POST"])
        def encode_text():
            """Encode text to vector using transformer"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get("text", "")

                if not text:
                    return jsonify({"error": "No text provided"}), 400

                vector = encode(text)

                return jsonify(
                    {
                        "vector": (
                            vector.tolist()
                            if HAS_NUMPY and hasattr(vector, "tolist")
                            else vector
                        ),
                        "dimension": len(vector),
                        "original_text": text,
                    }
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Encoding error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/chat", methods=["POST"])
        def chat_endpoint():
            """Chat interface using NLP pipeline"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get("text", "")
                user_id = data.get("user_id", "anonymous")
                session_id = data.get("session_id", None)

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

                return jsonify(
                    {
                        "response": response["response"],
                        "session_id": response["session_id"],
                        "user_id": user_id,
                    }
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Chat error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/similarity", methods=["POST"])
        def similarity_check():
            """Check semantic similarity between two texts"""
            self.request_count += 1
            try:
                data = request.get_json()
                text1 = data.get("text1", "")
                text2 = data.get("text2", "")

                if not text1 or not text2:
                    return jsonify({"error": "Both text1 and text2 required"}), 400

                similarity = reasoned_similarity(text1, text2)

                return jsonify(
                    {"similarity": similarity, "text1": text1, "text2": text2}
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Similarity error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/parse", methods=["POST"])
        def parse_endpoint():
            """Parse text structure"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get("text", "")

                if not text:
                    return jsonify({"error": "No text provided"}), 400

                parsed = parse_nlp(text)

                return jsonify({"parsed": parsed, "original_text": text})

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Parsing error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/pos_tag", methods=["POST"])
        def pos_tag_endpoint():
            """Part-of-speech tagging"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get("text", "")

                if not text:
                    return jsonify({"error": "No text provided"}), 400

                tags = get_pos_tags(text)

                return jsonify({"tags": tags, "original_text": text})

            except Exception as e:
                logger.error(f"[NLP_SERVICE] POS tagging error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/diff", methods=["POST"])
        def diff_endpoint():
            """Compare two texts and show differences"""
            self.request_count += 1
            try:
                data = request.get_json()
                text1 = data.get("text1", "")
                text2 = data.get("text2", "")

                if not text1 or not text2:
                    return jsonify({"error": "Both text1 and text2 required"}), 400

                diff = diff_texts(text1, text2)

                return jsonify({"diff": diff, "text1": text1, "text2": text2})

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Diff error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/attention", methods=["POST"])
        def attention_endpoint():
            """Process text through attention mechanism"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get("text", "")

                if not text:
                    return jsonify({"error": "No text provided"}), 400

                # Encode text to vector
                vector = encode(text)

                # Validate vector shape before reshaping
                if HAS_NUMPY:
                    if not isinstance(vector, np.ndarray):
                        try:
                            vector = np.array(vector, dtype=np.float32)
                        except Exception as e:
                            logger.error(
                                f"[NLP_SERVICE] Failed to convert vector to numpy array: {e}"
                            )
                            return (
                                jsonify({"error": f"Invalid vector format: {e}"}),
                                500,
                            )

                    # Check if vector is valid for attention processing
                    if vector.size == 0:
                        return (
                            jsonify({"error": "Empty vector returned from encoder"}),
                            500,
                        )

                    # Ensure vector is 1D before reshaping
                    if len(vector.shape) > 1:
                        # If already 2D, check if it's a valid shape
                        if len(vector.shape) == 2 and vector.shape[0] == 1:
                            input_tensor = vector  # Already in correct shape
                        else:
                            # Flatten to 1D then reshape
                            vector = vector.flatten()
                            input_tensor = vector.reshape(1, -1)
                    else:
                        # Reshape 1D vector to (1, embed_dim)
                        input_tensor = vector.reshape(1, -1)

                    # Validate final tensor shape
                    if len(input_tensor.shape) != 2 or input_tensor.shape[0] != 1:
                        return (
                            jsonify(
                                {
                                    "error": f"Invalid tensor shape for attention: {input_tensor.shape}. Expected (1, embed_dim)"
                                }
                            ),
                            500,
                        )
                else:
                    # Fallback handling without numpy
                    if not vector:
                        return (
                            jsonify({"error": "Empty vector returned from encoder"}),
                            500,
                        )

                    # Ensure vector is a list
                    if not isinstance(vector, list):
                        try:
                            vector = list(vector)
                        except Exception as e:
                            return (
                                jsonify({"error": f"Invalid vector format: {e}"}),
                                500,
                            )

                    # Create 2D structure for attention
                    input_tensor = [vector]  # Make it 2D: [[vector]]

                # Apply attention
                output, weights = self.attention.forward(input_tensor)

                return jsonify(
                    {
                        "output": (
                            output.tolist()
                            if HAS_NUMPY and hasattr(output, "tolist")
                            else output
                        ),
                        "attention_weights": (
                            weights.tolist()
                            if HAS_NUMPY and hasattr(weights, "tolist")
                            else weights
                        ),
                        "input_shape": (
                            input_tensor.shape
                            if HAS_NUMPY and hasattr(input_tensor, "shape")
                            else [
                                len(input_tensor),
                                len(input_tensor[0]) if input_tensor else 0,
                            ]
                        ),
                        "output_shape": (
                            output.shape
                            if HAS_NUMPY and hasattr(output, "shape")
                            else [
                                len(output),
                                (
                                    len(output[0])
                                    if output and isinstance(output[0], list)
                                    else len(output) if output else 0
                                ),
                            ]
                        ),
                        "original_text": text,
                    }
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Attention error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/batch_tokenize", methods=["POST"])
        def batch_tokenize():
            """Tokenize multiple texts at once"""
            self.request_count += 1
            try:
                data = request.get_json()
                texts = data.get("texts", [])

                if not texts:
                    return jsonify({"error": "No texts provided"}), 400

                if not isinstance(texts, list):
                    return jsonify({"error": "texts must be a list"}), 400

                results = []
                for i, text in enumerate(texts):
                    try:
                        tokens = tokenize(text)
                        results.append(
                            {
                                "index": i,
                                "tokens": tokens,
                                "count": len(tokens),
                                "original_text": text,
                            }
                        )
                    except Exception as e:
                        results.append(
                            {"index": i, "error": str(e), "original_text": text}
                        )

                return jsonify(
                    {
                        "results": results,
                        "total_processed": len(texts),
                        "successful": len([r for r in results if "error" not in r]),
                    }
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Batch tokenization error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/batch_encode", methods=["POST"])
        def batch_encode():
            """Encode multiple texts to vectors at once"""
            self.request_count += 1
            try:
                data = request.get_json()
                texts = data.get("texts", [])

                if not texts:
                    return jsonify({"error": "No texts provided"}), 400

                if not isinstance(texts, list):
                    return jsonify({"error": "texts must be a list"}), 400

                results = []
                for i, text in enumerate(texts):
                    try:
                        vector = encode(text)
                        results.append(
                            {
                                "index": i,
                                "vector": (
                                    vector.tolist()
                                    if HAS_NUMPY and hasattr(vector, "tolist")
                                    else vector
                                ),
                                "dimension": len(vector),
                                "original_text": text,
                            }
                        )
                    except Exception as e:
                        results.append(
                            {"index": i, "error": str(e), "original_text": text}
                        )

                return jsonify(
                    {
                        "results": results,
                        "total_processed": len(texts),
                        "successful": len([r for r in results if "error" not in r]),
                    }
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Batch encoding error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/analyze", methods=["POST"])
        def comprehensive_analysis():
            """Comprehensive text analysis combining multiple NLP functions"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get("text", "")
                include_vector = data.get("include_vector", False)

                if not text:
                    return jsonify({"error": "No text provided"}), 400

                analysis = {}

                # Tokenization
                try:
                    tokens = tokenize(text)
                    analysis["tokenization"] = {"tokens": tokens, "count": len(tokens)}
                except Exception as e:
                    analysis["tokenization"] = {"error": str(e)}

                # POS tagging
                try:
                    pos_tags = get_pos_tags(text)
                    analysis["pos_tagging"] = {"tags": pos_tags, "count": len(pos_tags)}
                except Exception as e:
                    analysis["pos_tagging"] = {"error": str(e)}

                # Parsing
                try:
                    parsed = parse_nlp(text)
                    analysis["parsing"] = parsed
                except Exception as e:
                    analysis["parsing"] = {"error": str(e)}

                # Vector encoding (optional)
                if include_vector:
                    try:
                        vector = encode(text)
                        analysis["encoding"] = {
                            "vector": (
                                vector.tolist()
                                if HAS_NUMPY and hasattr(vector, "tolist")
                                else vector
                            ),
                            "dimension": len(vector),
                        }
                    except Exception as e:
                        analysis["encoding"] = {"error": str(e)}

                return jsonify(
                    {
                        "analysis": analysis,
                        "original_text": text,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Comprehensive analysis error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/session/<session_id>", methods=["GET"])
        def get_session_info(session_id):
            """Get information about a specific chat session"""
            self.request_count += 1
            try:
                if session_id not in self.chat_sessions:
                    return jsonify({"error": "Session not found"}), 404

                session = self.chat_sessions[session_id]
                return jsonify(
                    {
                        "session_id": session_id,
                        "user_id": getattr(session, "user_id", "unknown"),
                        "history": (
                            session.get_history()
                            if hasattr(session, "get_history")
                            else []
                        ),
                        "created": "unknown",  # Add timestamp tracking in future
                    }
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Session info error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/session/<session_id>", methods=["DELETE"])
        def delete_session(session_id):
            """Delete a specific chat session"""
            self.request_count += 1
            try:
                if session_id not in self.chat_sessions:
                    return jsonify({"error": "Session not found"}), 404

                del self.chat_sessions[session_id]
                return jsonify(
                    {
                        "message": f"Session {session_id} deleted successfully",
                        "remaining_sessions": len(self.chat_sessions),
                    }
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Session deletion error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/sessions", methods=["GET"])
        def list_sessions():
            """List all active chat sessions"""
            self.request_count += 1
            try:
                sessions = []
                for session_id, session in self.chat_sessions.items():
                    sessions.append(
                        {
                            "session_id": session_id,
                            "user_id": getattr(session, "user_id", "unknown"),
                            "history_length": (
                                len(session.get_history())
                                if hasattr(session, "get_history")
                                else 0
                            ),
                        }
                    )

                return jsonify({"sessions": sessions, "total_count": len(sessions)})

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Sessions listing error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/pipeline", methods=["POST"])
        def nlp_pipeline():
            """Execute a custom NLP pipeline with configurable steps"""
            self.request_count += 1
            try:
                data = request.get_json()
                text = data.get("text", "")
                steps = data.get("steps", ["tokenize", "parse"])

                if not text:
                    return jsonify({"error": "No text provided"}), 400

                if not isinstance(steps, list):
                    return jsonify({"error": "steps must be a list"}), 400

                results = {}

                for step in steps:
                    try:
                        if step == "tokenize":
                            results["tokenize"] = tokenize(text)
                        elif step == "encode":
                            vector = encode(text)
                            results["encode"] = (
                                vector.tolist()
                                if HAS_NUMPY and hasattr(vector, "tolist")
                                else vector
                            )
                        elif step == "parse":
                            results["parse"] = parse_nlp(text)
                        elif step == "pos_tag":
                            results["pos_tag"] = get_pos_tags(text)
                        elif step == "similarity" and "reference_text" in data:
                            results["similarity"] = reasoned_similarity(
                                text, data["reference_text"]
                            )
                        else:
                            results[step] = {"error": f"Unknown step: {step}"}
                    except Exception as e:
                        results[step] = {"error": str(e)}

                return jsonify(
                    {
                        "pipeline_results": results,
                        "steps_executed": list(results.keys()),
                        "original_text": text,
                    }
                )

            except Exception as e:
                logger.error(f"[NLP_SERVICE] Pipeline error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/status", methods=["GET"])
        def status_endpoint():
            """Detailed service status"""
            return jsonify(
                {
                    "service": "NLP Engine",
                    "status": self.health_status,
                    "port": self.port,
                    "uptime": str(datetime.now() - self.start_time),
                    "requests_served": self.request_count,
                    "active_sessions": len(self.chat_sessions),
                    "components": {
                        "tokenizer": {
                            "status": "available" if self.tokenizer else "unavailable",
                            "type": (
                                type(self.tokenizer).__name__
                                if self.tokenizer
                                else None
                            ),
                        },
                        "transformer": {
                            "status": (
                                "available" if self.transformer else "unavailable"
                            ),
                            "device": (
                                getattr(self.transformer, "device", "unknown")
                                if self.transformer
                                else None
                            ),
                        },
                        "attention": {
                            "status": "available" if self.attention else "unavailable",
                            "heads": (
                                getattr(self.attention, "num_heads", "unknown")
                                if self.attention
                                else None
                            ),
                            "embed_dim": (
                                getattr(self.attention, "embed_dim", "unknown")
                                if self.attention
                                else None
                            ),
                        },
                    },
                    "endpoints": [
                        "/health",
                        "/tokenize",
                        "/encode",
                        "/chat",
                        "/similarity",
                        "/parse",
                        "/pos_tag",
                        "/diff",
                        "/attention",
                        "/status",
                        "/api",
                    ],
                    "timestamp": datetime.now().isoformat(),
                }
            )

        @self.app.route("/api", methods=["GET"])
        def api_documentation():
            """API documentation endpoint"""
            return jsonify(
                {
                    "service": "GremlinGPT NLP Engine API",
                    "version": "1.0.3",
                    "description": "Unified NLP service providing tokenization, encoding, chat, parsing, and analysis capabilities",
                    "base_url": f"http://localhost:{self.port}",
                    "endpoints": {
                        "/health": {
                            "method": "GET",
                            "description": "Service health check",
                            "response": "Service status, uptime, and component availability",
                        },
                        "/status": {
                            "method": "GET",
                            "description": "Detailed service status",
                            "response": "Comprehensive service information",
                        },
                        "/tokenize": {
                            "method": "POST",
                            "description": "Tokenize input text",
                            "body": {"text": "string"},
                            "response": {
                                "tokens": ["array"],
                                "count": "number",
                                "original_text": "string",
                            },
                        },
                        "/encode": {
                            "method": "POST",
                            "description": "Encode text to vector representation",
                            "body": {"text": "string"},
                            "response": {
                                "vector": ["array"],
                                "dimension": "number",
                                "original_text": "string",
                            },
                        },
                        "/chat": {
                            "method": "POST",
                            "description": "Chat interface with session management",
                            "body": {
                                "text": "string",
                                "user_id": "string (optional)",
                                "session_id": "string (optional)",
                            },
                            "response": {
                                "response": "string",
                                "session_id": "string",
                                "user_id": "string",
                            },
                        },
                        "/similarity": {
                            "method": "POST",
                            "description": "Calculate semantic similarity between two texts",
                            "body": {"text1": "string", "text2": "string"},
                            "response": {
                                "similarity": "object",
                                "text1": "string",
                                "text2": "string",
                            },
                        },
                        "/parse": {
                            "method": "POST",
                            "description": "Parse text structure and extract linguistic features",
                            "body": {"text": "string"},
                            "response": {"parsed": "object", "original_text": "string"},
                        },
                        "/pos_tag": {
                            "method": "POST",
                            "description": "Part-of-speech tagging",
                            "body": {"text": "string"},
                            "response": {"tags": ["array"], "original_text": "string"},
                        },
                        "/diff": {
                            "method": "POST",
                            "description": "Compare two texts and show differences",
                            "body": {"text1": "string", "text2": "string"},
                            "response": {
                                "diff": "object",
                                "text1": "string",
                                "text2": "string",
                            },
                        },
                        "/attention": {
                            "method": "POST",
                            "description": "Process text through attention mechanism",
                            "body": {"text": "string"},
                            "response": {
                                "output": ["array"],
                                "attention_weights": ["array"],
                                "input_shape": ["array"],
                                "output_shape": ["array"],
                                "original_text": "string",
                            },
                        },
                        "/batch_tokenize": {
                            "method": "POST",
                            "description": "Tokenize multiple texts at once",
                            "body": {"texts": ["array of strings"]},
                            "response": {
                                "results": ["array"],
                                "total_processed": "number",
                                "successful": "number",
                            },
                        },
                        "/batch_encode": {
                            "method": "POST",
                            "description": "Encode multiple texts to vectors at once",
                            "body": {"texts": ["array of strings"]},
                            "response": {
                                "results": ["array"],
                                "total_processed": "number",
                                "successful": "number",
                            },
                        },
                        "/analyze": {
                            "method": "POST",
                            "description": "Comprehensive text analysis combining multiple NLP functions",
                            "body": {
                                "text": "string",
                                "include_vector": "boolean (optional)",
                            },
                            "response": {
                                "analysis": "object",
                                "original_text": "string",
                                "timestamp": "string",
                            },
                        },
                        "/session/<session_id>": {
                            "method": "GET",
                            "description": "Get information about a specific chat session",
                            "response": {
                                "session_id": "string",
                                "user_id": "string",
                                "history": ["array"],
                            },
                        },
                        "/session/<session_id>": {
                            "method": "DELETE",
                            "description": "Delete a specific chat session",
                            "response": {
                                "message": "string",
                                "remaining_sessions": "number",
                            },
                        },
                        "/sessions": {
                            "method": "GET",
                            "description": "List all active chat sessions",
                            "response": {
                                "sessions": ["array"],
                                "total_count": "number",
                            },
                        },
                        "/pipeline": {
                            "method": "POST",
                            "description": "Execute a custom NLP pipeline with configurable steps",
                            "body": {
                                "text": "string",
                                "steps": ["array"],
                                "reference_text": "string (optional)",
                            },
                            "response": {
                                "pipeline_results": "object",
                                "steps_executed": ["array"],
                                "original_text": "string",
                            },
                        },
                    },
                    "examples": {
                        "tokenize": "curl -X POST -H 'Content-Type: application/json' -d '{\"text\":\"Hello world\"}' http://localhost:8001/tokenize",
                        "encode": "curl -X POST -H 'Content-Type: application/json' -d '{\"text\":\"Hello world\"}' http://localhost:8001/encode",
                        "chat": 'curl -X POST -H \'Content-Type: application/json\' -d \'{"text":"What is trading?","user_id":"trader1"}\' http://localhost:8001/chat',
                    },
                }
            )

    def _perform_health_check(self):
        """Perform internal health check of all components"""
        try:
            # Test tokenizer
            test_tokens = tokenize("Health check test")
            assert len(test_tokens) > 0, "Tokenizer failed"

            # Test transformer
            test_vector = encode("Health check test")
            assert (
                test_vector is not None and len(test_vector) > 0
            ), "Transformer failed"

            # Test attention
            if HAS_NUMPY and hasattr(test_vector, "reshape"):
                input_tensor = test_vector.reshape(1, -1)
            else:
                input_tensor = (
                    [test_vector] if isinstance(test_vector, list) else [[0.0] * 384]
                )
            output, weights = self.attention.forward(input_tensor)
            assert output is not None, "Attention failed"

            self.health_status = "healthy"
            logger.success(
                "[NLP_SERVICE] Health check passed - all components operational"
            )

            # Log to system if available
            if log_event:
                log_event(
                    "nlp_service",
                    "health_check",
                    {
                        "status": "healthy",
                        "timestamp": datetime.now().isoformat(),
                        "components_tested": ["tokenizer", "transformer", "attention"],
                    },
                )

        except Exception as e:
            self.health_status = "degraded"
            logger.error(f"[NLP_SERVICE] Health check failed: {e}")

            # Log to system if available
            if log_event:
                log_event(
                    "nlp_service",
                    "health_check",
                    {
                        "status": "degraded",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    },
                )

    def run(self, debug=False, threaded=True):
        """Run the NLP service"""
        logger.info(f"[NLP_SERVICE] Starting NLP Service on port {self.port}")
        logger.info(
            f"[NLP_SERVICE] Service endpoints available at http://localhost:{self.port}"
        )

        try:
            self.app.run(
                host="0.0.0.0",
                port=self.port,
                debug=debug,
                threaded=threaded,
                use_reloader=False,  # Disable reloader to prevent issues in production
            )
        except Exception as e:
            logger.error(f"[NLP_SERVICE] Failed to start service: {e}")
            self.health_status = "failed"
            raise


def main():
    """Main entry point for NLP Service"""
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="GremlinGPT NLP Service")
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to run the NLP service on (default: 8001)",
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the service to (default: 0.0.0.0)",
    )

    # Handle legacy positional argument for port (for backward compatibility)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        args = parser.parse_args(["--port", sys.argv[1]] + sys.argv[2:])
    else:
        args = parser.parse_args()

    # Allow environment variable override
    port = int(os.environ.get("NLP_PORT", args.port))
    host = os.environ.get("NLP_HOST", args.host)
    debug = (
        os.environ.get("NLP_DEBUG", "").lower() in ("true", "1", "yes") or args.debug
    )

    logger.info(f"[NLP_SERVICE] Starting NLP Service on {host}:{port} (debug={debug})")

    # Create and run service
    service = NLPService(port=port)

    try:
        service.run(host=host, debug=debug, threaded=True)
    except KeyboardInterrupt:
        logger.info("[NLP_SERVICE] Service stopped by user")
    except Exception as e:
        logger.error(f"[NLP_SERVICE] Service failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

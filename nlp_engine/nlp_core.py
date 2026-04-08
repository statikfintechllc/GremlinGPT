#!/usr/bin/env python3

"""
GremlinGPT NLP Core
Custom NLP implementation - no external dependencies

This module provides custom NLP functionality without relying on
transformers, pytorch, or other heavy dependencies.
Built for autonomous operation.
"""

import logging
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class CustomTokenizer:
    """Custom tokenizer - no external dependencies"""
    
    def __init__(self):
        # Basic vocabulary for special tokens
        self.special_tokens = {
            '[PAD]': 0,
            '[UNK]': 1,
            '[CLS]': 2,
            '[SEP]': 3,
            '[MASK]': 4,
        }
        self.vocab = dict(self.special_tokens)
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}
        self.vocab_size = len(self.vocab)
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words and subwords"""
        if not text:
            return []
        
        # Clean text
        text = text.lower().strip()
        
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
        
        return tokens
    
    def encode(self, text: str, max_length: int = 512, add_special_tokens: bool = True) -> List[int]:
        """Encode text to token IDs"""
        tokens = self.tokenize(text)
        
        if add_special_tokens:
            tokens = ['[CLS]'] + tokens[:max_length-2] + ['[SEP]']
        else:
            tokens = tokens[:max_length]
        
        # Convert to IDs (build vocab on the fly)
        ids = []
        for token in tokens:
            if token not in self.vocab:
                self.vocab[token] = self.vocab_size
                self.reverse_vocab[self.vocab_size] = token
                self.vocab_size += 1
            ids.append(self.vocab[token])
        
        return ids
    
    def decode(self, ids: List[int]) -> str:
        """Decode token IDs to text"""
        tokens = [self.reverse_vocab.get(id, '[UNK]') for id in ids]
        # Remove special tokens and join
        tokens = [t for t in tokens if t not in self.special_tokens]
        return ' '.join(tokens)


class CustomEmbedder:
    """Custom embedding generator - no external dependencies"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.word_vectors = {}
    
    def _hash_word(self, word: str) -> List[float]:
        """Generate deterministic embedding from word using hashing"""
        # Use multiple hash functions to create embedding
        vector = []
        for i in range(self.dimension):
            # Simple hash-based pseudo-random generation
            hash_val = hash((word, i)) % 1000000
            # Normalize to [-1, 1]
            val = (hash_val / 500000.0) - 1.0
            vector.append(val)
        
        # Normalize vector to unit length
        magnitude = math.sqrt(sum(x*x for x in vector))
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        
        return vector
    
    def encode(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if not text:
            return [0.0] * self.dimension
        
        # Tokenize
        words = text.lower().split()
        
        if not words:
            return [0.0] * self.dimension
        
        # Get or generate word vectors
        word_vecs = []
        for word in words:
            if word not in self.word_vectors:
                self.word_vectors[word] = self._hash_word(word)
            word_vecs.append(self.word_vectors[word])
        
        # Average word vectors
        avg_vec = [0.0] * self.dimension
        for vec in word_vecs:
            for i in range(self.dimension):
                avg_vec[i] += vec[i]
        
        # Average
        for i in range(self.dimension):
            avg_vec[i] /= len(word_vecs)
        
        return avg_vec
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        mag1 = math.sqrt(sum(x * x for x in vec1))
        mag2 = math.sqrt(sum(x * x for x in vec2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)


class NLPCore:
    """
    Core NLP functionality with custom implementations.
    No external dependencies - fully autonomous.
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        
        # Initialize custom components
        self.tokenizer = CustomTokenizer()
        self.embedder = CustomEmbedder()
        
        logger.info("✓ Custom NLP core initialized (no external dependencies)")
    
    def tokenize(self, text: str, max_length: int = 512) -> List[str]:
        """
        Tokenize text into tokens
        
        Args:
            text: Input text
            max_length: Maximum number of tokens
            
        Returns:
            List of tokens
        """
        return self.tokenizer.tokenize(text)[:max_length]
    
    def encode(self, text: str, max_length: int = 512) -> List[int]:
        """
        Encode text to token IDs
        
        Args:
            text: Input text
            max_length: Maximum number of tokens
            
        Returns:
            List of token IDs
        """
        return self.tokenizer.encode(text, max_length=max_length)
    
    def get_embeddings(self, text: str) -> List[float]:
        """
        Get vector embeddings for text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        return self.embedder.encode(text)
    
    def get_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        emb1 = self.embedder.encode(text1)
        emb2 = self.embedder.encode(text2)
        
        # Cosine similarity, normalized to 0-1
        similarity = self.embedder.cosine_similarity(emb1, emb2)
        # Convert from [-1, 1] to [0, 1]
        return (similarity + 1) / 2
    
    def parse_command(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language command
        
        Args:
            text: Input command text
            
        Returns:
            Parsed command structure
        """
        text = text.strip().lower()
        
        # Basic command parsing
        result = {
            'original': text,
            'tokens': self.tokenize(text),
            'intent': self._extract_intent(text),
            'entities': self._extract_entities(text)
        }
        
        return result
    
    def _extract_intent(self, text: str) -> str:
        """Extract command intent"""
        text_lower = text.lower()
        
        # Intent keywords mapping
        intent_patterns = {
            'start': ['start', 'begin', 'launch', 'run', 'boot', 'init'],
            'stop': ['stop', 'halt', 'terminate', 'end', 'shutdown', 'kill'],
            'status': ['status', 'health', 'check', 'info', 'state'],
            'help': ['help', 'assist', 'guide', 'how', 'what', 'explain'],
            'restart': ['restart', 'reboot', 'reload'],
            'config': ['config', 'configure', 'settings', 'setup'],
        }
        
        # Check for intent patterns
        for intent, keywords in intent_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return intent
        
        # Default to chat/query
        return 'chat'
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        tokens = self.tokenizer.tokenize(text)
        
        # Simple entity extraction - capitalized words, quoted strings, etc.
        entities = []
        
        # Find quoted strings
        quoted = re.findall(r'"([^"]*)"', text) + re.findall(r"'([^']*)'", text)
        entities.extend(quoted)
        
        # Find capitalized words (potential proper nouns)
        for token in tokens:
            if token and len(token) > 1 and token[0].isupper():
                entities.append(token)
        
        return entities
    
    def get_pos_tags(self, text: str) -> List[tuple]:
        """
        Get part-of-speech tags for text (simple rule-based)
        
        Args:
            text: Input text
            
        Returns:
            List of (word, tag) tuples
        """
        tokens = self.tokenizer.tokenize(text)
        tags = []
        
        # Simple rule-based POS tagging
        for i, token in enumerate(tokens):
            tag = 'NOUN'  # Default
            
            # Simple heuristics
            if token in ['the', 'a', 'an']:
                tag = 'DET'
            elif token in ['is', 'are', 'was', 'were', 'be', 'been', 'being']:
                tag = 'VERB'
            elif token in ['and', 'or', 'but', 'so']:
                tag = 'CONJ'
            elif token in ['in', 'on', 'at', 'to', 'from', 'with', 'by']:
                tag = 'PREP'
            elif token.endswith('ly'):
                tag = 'ADV'
            elif token.endswith('ing') or token.endswith('ed'):
                tag = 'VERB'
            
            tags.append((token, tag))
        
        return tags
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health of NLP components
        
        Returns:
            Health status dictionary
        """
        status = {
            'healthy': True,
            'components': {},
            'mode': 'custom_implementation'
        }
        
        # Check tokenizer
        try:
            test_tokens = self.tokenize("test")
            status['components']['tokenizer'] = 'healthy' if test_tokens else 'degraded'
        except Exception as e:
            status['components']['tokenizer'] = f'failed: {e}'
            status['healthy'] = False
        
        # Check embedder
        try:
            test_emb = self.get_embeddings("test")
            status['components']['embeddings'] = 'healthy' if len(test_emb) > 0 else 'degraded'
        except Exception as e:
            status['components']['embeddings'] = f'failed: {e}'
            status['healthy'] = False
        
        return status


# Convenience functions for backward compatibility
_nlp_instance = None

def get_nlp_instance() -> NLPCore:
    """Get or create singleton NLP instance"""
    global _nlp_instance
    if _nlp_instance is None:
        _nlp_instance = NLPCore()
    return _nlp_instance


def tokenize(text: str, max_length: int = 512) -> List[str]:
    """Tokenize text"""
    return get_nlp_instance().tokenize(text, max_length)


def encode(text: str, max_length: int = 512) -> List[int]:
    """Encode text to token IDs"""
    return get_nlp_instance().encode(text, max_length)


def get_embeddings(text: str) -> List[float]:
    """Get embeddings for text"""
    return get_nlp_instance().get_embeddings(text)


def get_similarity(text1: str, text2: str) -> float:
    """Get similarity between texts"""
    return get_nlp_instance().get_similarity(text1, text2)


def parse_nlp(text: str) -> Dict[str, Any]:
    """Parse natural language command"""
    return get_nlp_instance().parse_command(text)


def get_pos_tags(text: str) -> List[tuple]:
    """Get POS tags for text"""
    return get_nlp_instance().get_pos_tags(text)

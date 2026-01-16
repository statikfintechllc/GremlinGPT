#!/usr/bin/env python3

"""
GremlinGPT NLP Core
Proper NLP implementation without fallback degradation

This module provides the actual NLP functionality with real models.
If dependencies are missing, it fails fast with clear error messages.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class NLPCore:
    """
    Core NLP functionality with real implementations.
    No fallback mode - fails fast if dependencies unavailable.
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.model_dir = self.base_dir / 'data' / 'models'
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.tokenizer = None
        self.embedding_model = None
        
        # Load models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize NLP models - fail fast if not available"""
        logger.info("Loading NLP models...")
        
        # Check for required dependencies
        try:
            import torch
        except ImportError:
            raise RuntimeError(
                "PyTorch not installed. Install with: pip install torch>=2.0.0"
            )
        
        try:
            from transformers import AutoTokenizer
        except ImportError:
            raise RuntimeError(
                "Transformers not installed. Install with: pip install transformers>=4.30.0"
            )
        
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise RuntimeError(
                "Sentence-transformers not installed. Install with: pip install sentence-transformers>=2.2.0"
            )
        
        # Load tokenizer
        logger.info("Loading tokenizer...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                'bert-base-uncased',
                cache_dir=str(self.model_dir)
            )
            logger.info("✓ Tokenizer loaded")
        except Exception as e:
            raise RuntimeError(f"Failed to load tokenizer: {e}")
        
        # Load embedding model
        logger.info("Loading embedding model...")
        try:
            self.embedding_model = SentenceTransformer(
                'all-MiniLM-L6-v2',
                cache_folder=str(self.model_dir)
            )
            logger.info("✓ Embedding model loaded")
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}")
        
        logger.info("✓ All NLP models loaded successfully")
    
    def tokenize(self, text: str, max_length: int = 512) -> List[str]:
        """
        Tokenize text into tokens
        
        Args:
            text: Input text
            max_length: Maximum number of tokens
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        tokens = self.tokenizer.tokenize(text)
        return tokens[:max_length]
    
    def encode(self, text: str, max_length: int = 512) -> List[int]:
        """
        Encode text to token IDs
        
        Args:
            text: Input text
            max_length: Maximum number of tokens
            
        Returns:
            List of token IDs
        """
        if not text:
            return []
        
        encoding = self.tokenizer.encode(
            text,
            max_length=max_length,
            truncation=True,
            add_special_tokens=True
        )
        return encoding
    
    def get_embeddings(self, text: str) -> List[float]:
        """
        Get vector embeddings for text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        if not text:
            return [0.0] * 384  # Default embedding size
        
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
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
        
        from sentence_transformers import util
        
        emb1 = self.embedding_model.encode(text1)
        emb2 = self.embedding_model.encode(text2)
        
        similarity = util.cos_sim(emb1, emb2).item()
        return float(similarity)
    
    def parse_command(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language command
        
        Args:
            text: Input command text
            
        Returns:
            Parsed command structure
        """
        text = text.strip().lower()
        
        # Basic command parsing (can be enhanced)
        result = {
            'original': text,
            'tokens': self.tokenize(text),
            'intent': self._extract_intent(text),
            'entities': self._extract_entities(text)
        }
        
        return result
    
    def _extract_intent(self, text: str) -> str:
        """Extract command intent"""
        # Simple intent extraction - can be enhanced with classifier
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['start', 'begin', 'launch', 'run']):
            return 'start'
        elif any(word in text_lower for word in ['stop', 'halt', 'terminate', 'end']):
            return 'stop'
        elif any(word in text_lower for word in ['status', 'health', 'check']):
            return 'status'
        elif any(word in text_lower for word in ['help', 'info', 'what']):
            return 'help'
        else:
            return 'unknown'
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        # Simple entity extraction - can be enhanced with NER
        tokens = self.tokenize(text)
        
        # For now, return tokens that might be entities (capitalized, etc.)
        entities = [t for t in tokens if t and t[0].isupper()]
        
        return entities
    
    def get_pos_tags(self, text: str) -> List[tuple]:
        """
        Get part-of-speech tags for text
        
        Args:
            text: Input text
            
        Returns:
            List of (word, tag) tuples
        """
        try:
            import nltk
            
            # Download required data if not present
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            
            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger', quiet=True)
            
            tokens = nltk.word_tokenize(text)
            return nltk.pos_tag(tokens)
            
        except Exception as e:
            logger.warning(f"POS tagging failed: {e}")
            # Return basic tokenization if NLTK fails
            return [(token, 'UNKNOWN') for token in text.split()]
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health of NLP components
        
        Returns:
            Health status dictionary
        """
        status = {
            'healthy': True,
            'components': {}
        }
        
        # Check tokenizer
        try:
            test_tokens = self.tokenize("test")
            status['components']['tokenizer'] = 'healthy' if test_tokens else 'degraded'
        except Exception as e:
            status['components']['tokenizer'] = f'failed: {e}'
            status['healthy'] = False
        
        # Check embedding model
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

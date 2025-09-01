#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: NLP Client Library
# Client library for interacting with the NLP Service API

import json
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime

class NLPClient:
    """
    Client library for interacting with the GremlinGPT NLP Service.
    Provides convenient methods for all NLP service endpoints.
    """
    
    def __init__(self, base_url: str = "http://localhost:8001", timeout: int = 30):
        """
        Initialize the NLP client.
        
        Args:
            base_url: Base URL of the NLP service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GremlinGPT-NLP-Client/1.0.3'
        })
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the NLP service.
        
        Args:
            endpoint: API endpoint (without leading slash)
            method: HTTP method
            data: Request data for POST requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.RequestException: For network/HTTP errors
            ValueError: For invalid JSON responses
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"NLP service request failed: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from NLP service: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the NLP service.
        
        Returns:
            Health status information
        """
        return self._make_request('health')
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get detailed status information about the NLP service.
        
        Returns:
            Detailed service status
        """
        return self._make_request('status')
    
    def get_api_docs(self) -> Dict[str, Any]:
        """
        Get API documentation from the NLP service.
        
        Returns:
            API documentation
        """
        return self._make_request('api')
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """
        Tokenize input text.
        
        Args:
            text: Text to tokenize
            
        Returns:
            Tokenization result with tokens, count, and original text
        """
        return self._make_request('tokenize', 'POST', {'text': text})
    
    def encode(self, text: str) -> Dict[str, Any]:
        """
        Encode text to vector representation.
        
        Args:
            text: Text to encode
            
        Returns:
            Vector encoding with vector, dimension, and original text
        """
        return self._make_request('encode', 'POST', {'text': text})
    
    def chat(self, text: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a chat message to the NLP service.
        
        Args:
            text: Message text
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            Chat response with response text, session_id, and user_id
        """
        data = {'text': text}
        if user_id:
            data['user_id'] = user_id
        if session_id:
            data['session_id'] = session_id
            
        return self._make_request('chat', 'POST', data)
    
    def similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity analysis result
        """
        return self._make_request('similarity', 'POST', {'text1': text1, 'text2': text2})
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse text structure and extract linguistic features.
        
        Args:
            text: Text to parse
            
        Returns:
            Parsing result with linguistic analysis
        """
        return self._make_request('parse', 'POST', {'text': text})
    
    def pos_tag(self, text: str) -> Dict[str, Any]:
        """
        Perform part-of-speech tagging on text.
        
        Args:
            text: Text to tag
            
        Returns:
            POS tagging result
        """
        return self._make_request('pos_tag', 'POST', {'text': text})
    
    def diff(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Compare two texts and show differences.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Diff analysis result
        """
        return self._make_request('diff', 'POST', {'text1': text1, 'text2': text2})
    
    def attention(self, text: str) -> Dict[str, Any]:
        """
        Process text through attention mechanism.
        
        Args:
            text: Text to process
            
        Returns:
            Attention processing result with weights and output
        """
        return self._make_request('attention', 'POST', {'text': text})
    
    def is_available(self) -> bool:
        """
        Check if the NLP service is available.
        
        Returns:
            True if service is available and healthy, False otherwise
        """
        try:
            health = self.health_check()
            return health.get('status') == 'healthy'
        except Exception:
            return False
    
    def wait_for_service(self, max_attempts: int = 30, delay: float = 1.0) -> bool:
        """
        Wait for the NLP service to become available.
        
        Args:
            max_attempts: Maximum number of attempts
            delay: Delay between attempts in seconds
            
        Returns:
            True if service becomes available, False if timeout
        """
        import time
        
        for attempt in range(max_attempts):
            if self.is_available():
                return True
            time.sleep(delay)
        
        return False

# Convenience functions for quick access
def create_client(base_url: str = "http://localhost:8001") -> NLPClient:
    """Create a new NLP client instance."""
    return NLPClient(base_url)

def quick_tokenize(text: str, base_url: str = "http://localhost:8001") -> List[str]:
    """Quickly tokenize text and return just the tokens list."""
    client = NLPClient(base_url)
    result = client.tokenize(text)
    return result.get('tokens', [])

def quick_encode(text: str, base_url: str = "http://localhost:8001") -> List[float]:
    """Quickly encode text and return just the vector."""
    client = NLPClient(base_url)
    result = client.encode(text)
    return result.get('vector', [])

def quick_chat(text: str, base_url: str = "http://localhost:8001") -> str:
    """Quickly send a chat message and return just the response text."""
    client = NLPClient(base_url)
    result = client.chat(text)
    return result.get('response', '')

# Example usage
if __name__ == "__main__":
    # Create client
    client = NLPClient()
    
    # Check if service is available
    if not client.is_available():
        print("NLP service is not available. Please start the service first.")
        exit(1)
    
    # Test basic functionality
    print("=== NLP Client Test ===")
    
    # Health check
    health = client.health_check()
    print(f"Service Status: {health.get('status')}")
    
    # Tokenization
    text = "Hello, this is a test of the GremlinGPT NLP service!"
    tokens = client.tokenize(text)
    print(f"Tokens: {tokens.get('tokens')}")
    
    # Encoding
    encoding = client.encode(text)
    print(f"Vector dimension: {encoding.get('dimension')}")
    
    # Chat
    chat_response = client.chat("What is natural language processing?", user_id="test_user")
    print(f"Chat response: {chat_response.get('response')}")
    
    # Parse
    parsed = client.parse(text)
    print(f"Parse route: {parsed.get('parsed', {}).get('route', 'unknown')}")
    
    print("=== Test Complete ===")
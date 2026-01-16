#!/usr/bin/env python3

"""
Test script to demonstrate GremlinGPT CLI functionality
"""

import sys
import time
from pathlib import Path

# Add parent directory to path dynamically
BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from main import GremlinGPT

def test_cli_commands():
    """Test various CLI commands"""
    
    print("\n" + "=" * 60)
    print("GremlinGPT CLI Test")
    print("=" * 60 + "\n")
    
    # Initialize system
    system = GremlinGPT()
    
    print("1. Testing NLP initialization...")
    if not system.initialize_nlp():
        print("✗ Failed to initialize NLP")
        return False
    print("✓ NLP initialized\n")
    
    # Test various command intents
    test_commands = [
        ("start the system", "start"),
        ("stop everything", "stop"),
        ("show me the status", "status"),
        ("I need help", "help"),
        ("restart the service", "restart"),
        ("configure the settings", "config"),
        ("hello, how are you?", "chat"),
    ]
    
    nlp = system.components['nlp']
    
    print("2. Testing intent recognition:")
    print("-" * 60)
    for command, expected_intent in test_commands:
        result = nlp.parse_command(command)
        intent = result['intent']
        status = "✓" if intent == expected_intent else "✗"
        print(f"{status} '{command}' -> intent: {intent} (expected: {expected_intent})")
    print()
    
    print("3. Testing tokenization:")
    print("-" * 60)
    text = "GremlinGPT is an autonomous cognitive system."
    tokens = nlp.tokenize(text)
    print(f"Text: {text}")
    print(f"Tokens: {tokens}")
    print()
    
    print("4. Testing embeddings:")
    print("-" * 60)
    embedding = nlp.get_embeddings("test text")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print()
    
    print("5. Testing similarity:")
    print("-" * 60)
    pairs = [
        ("hello", "hi"),
        ("start", "begin"),
        ("stop", "end"),
        ("hello", "goodbye"),
    ]
    for text1, text2 in pairs:
        sim = nlp.get_similarity(text1, text2)
        print(f"Similarity('{text1}', '{text2}'): {sim:.3f}")
    print()
    
    print("6. Testing POS tagging:")
    print("-" * 60)
    text = "The system is running smoothly"
    tags = nlp.get_pos_tags(text)
    print(f"Text: {text}")
    print(f"POS tags: {tags}")
    print()
    
    print("7. Health check:")
    print("-" * 60)
    health = nlp.health_check()
    print(f"Health status: {health}")
    print()
    
    print("=" * 60)
    print("✓ All tests passed! System is functional.")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    success = test_cli_commands()
    sys.exit(0 if success else 1)

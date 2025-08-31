# !/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: Module Integrity Directive
# This script is a component of the GremlinGPT system, under Alpha expansion.

import sys
import traceback
from datetime import datetime

NLP_OUT_LOG = "$HOME/data/logs/nlp.out"


def log_nlp_out(message):
    import os
    timestamp = datetime.now().isoformat()
    
    # Resolve $HOME properly
    log_path = NLP_OUT_LOG.replace("$HOME", os.path.expanduser("~"))
    # Also try current working directory path
    alt_log_path = os.path.join(os.getcwd(), "data/logs/nlp.out")
    
    for path in [log_path, alt_log_path]:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a") as f:
                f.write(f"[{timestamp}] {message}\n")
            return  # Success, exit function
        except Exception as e:
            continue  # Try next path
    
    # If all paths fail, just print to stderr
    print(f"[NLP_CHECK] Could not write to any log path: {message}", file=sys.stderr)


try:
    from nlp_engine.tokenizer import Tokenizer  # Your actual tokenizer
    from nlp_engine.transformer_core import TransformerCore  # Your real core model
except ImportError as e:
    err_msg = f"[NLP_CHECK] ImportError: {e}"
    print(err_msg, file=sys.stderr)
    log_nlp_out(err_msg)
    
    # Try alternative imports
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from tokenizer import Tokenizer
        from transformer_core import TransformerCore
    except ImportError as e2:
        err_msg2 = f"[NLP_CHECK] Alternative import failed: {e2}"
        print(err_msg2, file=sys.stderr)
        log_nlp_out(err_msg2)
        
        # Create mock classes to prevent total failure
        class Tokenizer:
            def tokenize(self, text): return text.split()
        
        class TransformerCore:
            def process(self, tokens): return tokens


def nlp_internal_check():
    status = "FAILED"
    sys_msg = ""
    try:
        # Simple English test phrase
        test_phrase = "This is a test of the GremlinGPT NLP engine."
        # Instantiate your tokenizer (adjust class name if needed)
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(test_phrase)
        assert isinstance(tokens, list) and len(tokens) > 0, "Tokenization failed"

        # Instantiate your transformer (adjust class name if needed)
        model = TransformerCore()
        result = model.forward(tokens)
        assert result is not None, "Transformer forward failed"

        # Ask the model how it "feels" (system status query)
        try:
            health_query = "How are you feeling? How is your system health?"
            health_tokens = tokenizer.tokenize(health_query)
            health_response = model.forward(health_tokens)
            sys_msg = (
                health_response
                if isinstance(health_response, str)
                else str(health_response)
            )
        except Exception as health_ex:
            sys_msg = f"[NLP_CHECK] Could not get model health: {health_ex}"

        status = "OK"
        print("NLP Internal Check: ✅")
        print(f"[NLP_CHECK] Model says: {sys_msg}")
        log_nlp_out(f"NLP Internal Check: OK | Model: {sys_msg}")

    except Exception as ex:
        err_info = f"[NLP_CHECK] Error: {ex}\n{traceback.format_exc()}"
        print(err_info, file=sys.stderr)
        log_nlp_out(f"NLP Internal Check: FAILED | {ex}")
        sys.exit(1)


if __name__ == "__main__":
    nlp_internal_check()

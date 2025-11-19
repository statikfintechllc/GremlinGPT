#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

# GremlinGPT v1.0.3 :: utils/nltk_setup.py :: Module Integrity Directive
# Self-improving NLTK setup for GremlinGPT.
# This script is a component of the GremlinGPT system, under Alpha expansion.

import os
import sys

# Try to import NLTK, but don't fail if it's not available
try:
    import nltk

    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    nltk = None


def setup_nltk_data():
    """
    Ensures that the required NLTK data (such as 'punkt') is available by checking
    specified directories and downloading missing resources if necessary.
    Only uses the project's data/nltk_data directory.

    Returns:
        str: The absolute path to the base NLTK data directory used, or None if NLTK not available
    """
    if not HAS_NLTK:
        print("[NLTK] NLTK module not available. Install with: pip install nltk")
        return None

    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "nltk_data")
    )

    # Ensure the directory exists with proper permissions
    try:
        os.makedirs(base_dir, exist_ok=True)
        # Verify write permissions
        test_file = os.path.join(base_dir, ".test_write")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        print(f"[NLTK] Warning: Cannot write to {base_dir}: {e}")
        # Fall back to user's NLTK data directory if project dir not writable
        import tempfile

        base_dir = os.path.join(tempfile.gettempdir(), "gremlin_nltk_data")
        os.makedirs(base_dir, exist_ok=True)
        print(f"[NLTK] Using fallback directory: {base_dir}")

    # Clear default NLTK data paths and set only our project directory
    nltk.data.path.clear()
    nltk.data.path.append(base_dir)

    # Set NLTK_DATA environment variable to prevent downloads to $HOME
    os.environ["NLTK_DATA"] = base_dir

    # Comprehensive list of required NLTK resources
    required_resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/omw-1.4", "omw-1.4"),  # Open Multilingual Wordnet
    ]

    success_count = 0
    failed_resources = []

    for resource_path, resource_name in required_resources:
        try:
            nltk.data.find(resource_path)
            print(f"[NLTK] ✓ Found {resource_name}")
            success_count += 1
        except LookupError:
            print(f"[NLTK] → Downloading {resource_name}...")
            try:
                nltk.download(resource_name, download_dir=base_dir, quiet=False)
                print(f"[NLTK] ✓ Successfully downloaded {resource_name}")
                success_count += 1
            except Exception as e:
                print(f"[NLTK] ✗ Failed to download {resource_name}: {e}")
                failed_resources.append(resource_name)
        except Exception as e:
            print(f"[NLTK] ✗ Error checking {resource_name}: {e}")
            failed_resources.append(resource_name)

    # Print summary
    print(f"\n[NLTK] Setup Summary:")
    print(f"  ✓ Successfully loaded: {success_count}/{len(required_resources)}")
    if failed_resources:
        print(f"  ✗ Failed resources: {', '.join(failed_resources)}")
    print(f"  📁 Data directory: {base_dir}\n")

    return base_dir


def validate_nltk_installation():
    """
    Validates that NLTK is properly installed and all required resources are available.

    Returns:
        dict: Status information about NLTK installation
    """
    status = {
        "nltk_available": HAS_NLTK,
        "nltk_version": None,
        "data_path": None,
        "resources_available": {},
        "all_resources_ready": False,
    }

    if not HAS_NLTK:
        return status

    status["nltk_version"] = nltk.__version__

    # Setup NLTK data first
    data_path = setup_nltk_data()
    status["data_path"] = data_path

    # Check each resource
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/omw-1.4", "omw-1.4"),
    ]

    for resource_path, resource_name in resources:
        try:
            nltk.data.find(resource_path)
            status["resources_available"][resource_name] = True
        except LookupError:
            status["resources_available"][resource_name] = False

    status["all_resources_ready"] = all(status["resources_available"].values())

    return status


def get_nltk_data_path():
    """
    Returns the NLTK data path for use by other modules.

    Returns:
        str: Path to NLTK data directory
    """
    if not HAS_NLTK:
        return None

    # Check if already set up
    nltk_data_env = os.environ.get("NLTK_DATA")
    if nltk_data_env and os.path.exists(nltk_data_env):
        return nltk_data_env

    # Otherwise, set it up
    return setup_nltk_data()


# Auto-setup when module is imported (but don't fail if NLTK unavailable)
if HAS_NLTK and __name__ != "__main__":
    try:
        setup_nltk_data()
    except Exception as e:
        print(f"[NLTK] Warning: Auto-setup failed: {e}")


if __name__ == "__main__":
    # When run as a script, perform full validation
    print("=" * 60)
    print("NLTK Setup and Validation Tool")
    print("=" * 60)

    if not HAS_NLTK:
        print("\n[ERROR] NLTK is not installed!")
        print("Install it with: pip install nltk")
        sys.exit(1)

    status = validate_nltk_installation()

    print("\nValidation Results:")
    print(f"  NLTK Version: {status['nltk_version']}")
    print(f"  Data Path: {status['data_path']}")
    print(f"\nResource Status:")
    for resource, available in status["resources_available"].items():
        symbol = "✓" if available else "✗"
        print(f"    {symbol} {resource}")

    if status["all_resources_ready"]:
        print("\n✓ All NLTK resources are ready!")
        sys.exit(0)
    else:
        print(
            "\n✗ Some NLTK resources are missing. Run setup_nltk_data() to download them."
        )
        sys.exit(1)

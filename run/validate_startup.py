#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────
# ⚠️ GremlinGPT Fair Use Only | Commercial Use Requires License
# Built under the GremlinGPT Dual License v1.0
# © 2025 StatikFintechLLC / AscendAI Project
# Contact: ascend.gremlin@gmail.com
# ─────────────────────────────────────────────────────────────

"""
GremlinGPT Startup Validation Script
Validates that all dependencies and services are ready to launch
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_nltk_setup():
    """Check NLTK setup and resources"""
    print_section("NLTK Setup Validation")

    try:
        from utils.nltk_setup import validate_nltk_installation

        status = validate_nltk_installation()

        print(f"NLTK Available: {'✓' if status['nltk_available'] else '✗'}")
        if status["nltk_available"]:
            print(f"NLTK Version: {status['nltk_version']}")
            print(f"Data Path: {status['data_path']}")
            print("\nResource Status:")
            for resource, available in status["resources_available"].items():
                symbol = "✓" if available else "✗"
                print(f"  {symbol} {resource}")

            if status["all_resources_ready"]:
                print("\n✅ All NLTK resources are ready")
                return True
            else:
                print("\n⚠️  Some NLTK resources are missing")
                return False
        else:
            print("\n⚠️  NLTK is not installed")
            return False
    except Exception as e:
        print(f"✗ Error checking NLTK: {e}")
        return False


def check_environments():
    """Check all conda environments"""
    print_section("Environment Validation")

    environments = {
        "dashboard": "conda_envs.environments.dashboard.globals",
        "memory": "conda_envs.environments.memory.globals",
        "nlp": "conda_envs.environments.nlp.globals",
        "orchestrator": "conda_envs.environments.orchestrator.globals",
        "scraper": "conda_envs.environments.scraper.globals",
    }

    results = {}
    for env_name, env_module in environments.items():
        try:
            __import__(env_module, fromlist=["*"])
            print(f"✓ {env_name}: OK")
            results[env_name] = True
        except Exception as e:
            print(f"✗ {env_name}: FAILED - {e}")
            results[env_name] = False

    all_ok = all(results.values())
    print(
        f"\n{'✅' if all_ok else '⚠️'} Environment Check: {sum(results.values())}/{len(results)} passed"
    )
    return all_ok


def check_key_modules():
    """Check if key modules can be imported"""
    print_section("Key Module Validation")

    modules = [
        ("NLP Service", "nlp_engine.nlp_service"),
        ("Memory Embedder", "memory.vector_store.embedder"),
        ("Scraper Loop", "scraper.scraper_loop"),
        ("Core Loop", "core.loop"),
        ("FSM Agent", "agent_core.fsm"),
        ("Backend Server", "backend.server"),
    ]

    results = {}
    for name, module_path in modules:
        try:
            __import__(module_path)
            print(f"✓ {name}: OK")
            results[name] = True
        except Exception as e:
            print(f"✗ {name}: FAILED - {str(e)[:60]}")
            results[name] = False

    all_ok = all(results.values())
    print(
        f"\n{'✅' if all_ok else '⚠️'} Module Check: {sum(results.values())}/{len(results)} passed"
    )
    return all_ok


def check_dependencies():
    """Check critical Python dependencies"""
    print_section("Dependency Validation")

    dependencies = {
        "flask": "Flask web framework",
        "numpy": "Numerical computing",
        "nltk": "Natural language toolkit",
        "sentence_transformers": "Sentence embeddings",
        "transformers": "Hugging Face transformers",
        "requests": "HTTP library",
        "playwright": "Browser automation",
        "chromadb": "Vector database",
        "faiss": "Vector similarity search",
    }

    results = {}
    for dep_name, description in dependencies.items():
        try:
            __import__(dep_name)
            print(f"✓ {dep_name}: OK ({description})")
            results[dep_name] = True
        except ImportError:
            print(f"⚠  {dep_name}: MISSING ({description})")
            results[dep_name] = False

    installed = sum(results.values())
    print(
        f"\n{'✅' if installed >= 6 else '⚠️'} Dependencies: {installed}/{len(results)} installed"
    )
    return installed >= 6  # At least core deps should be present


def check_data_directories():
    """Check if required data directories exist"""
    print_section("Data Directory Validation")

    required_dirs = [
        "data",
        "data/logs",
        "data/nltk_data",
        "data/nlp_training_sets",
        "data/embeddings",
        "config",
    ]

    results = {}
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        exists = full_path.exists()
        results[dir_path] = exists
        symbol = "✓" if exists else "✗"
        print(f"{symbol} {dir_path}: {'OK' if exists else 'MISSING'}")

    all_ok = all(results.values())
    print(
        f"\n{'✅' if all_ok else '⚠️'} Directory Check: {sum(results.values())}/{len(results)} exist"
    )
    return all_ok


def main():
    """Run all validation checks"""
    print("\n" + "=" * 70)
    print("  GremlinGPT Startup Validation")
    print("  Checking dependencies and configuration...")
    print("=" * 70)

    # Run all checks
    checks = {
        "NLTK Setup": check_nltk_setup(),
        "Environments": check_environments(),
        "Key Modules": check_key_modules(),
        "Dependencies": check_dependencies(),
        "Data Directories": check_data_directories(),
    }

    # Print summary
    print_section("Validation Summary")

    for check_name, passed in checks.items():
        symbol = "✅" if passed else "⚠️"
        print(f"{symbol} {check_name}: {'PASSED' if passed else 'FAILED'}")

    total_passed = sum(checks.values())
    total_checks = len(checks)

    print(f"\nOverall: {total_passed}/{total_checks} checks passed")

    if total_passed == total_checks:
        print("\n✅ System is ready for startup!")
        return 0
    elif total_passed >= 3:
        print("\n⚠️  System may start with degraded functionality")
        return 1
    else:
        print("\n❌ Critical issues detected, startup may fail")
        return 2


if __name__ == "__main__":
    sys.exit(main())

#!/bin/bash

echo "[GremlinGPT] Creating conda environments..."

cd "$(dirname "$0")" # Always run from conda_envs/

ENV_NAMES=(
  "gremlin-nlp"
  "gremlin-dashboard"
  "gremlin-scraper"
  "gremlin-memory"
  "gremlin-orchestrator"
)

# Due to network timeouts with pip, create minimal environments
for ENV in "${ENV_NAMES[@]}"; do
  echo "[INFO] Checking environment: $ENV"

  if conda info --envs | awk '{print $1}' | grep -qx "$ENV"; then
    echo "[SKIP] Environment '$ENV' already exists."
    continue
  fi

  echo "[CREATE] Creating minimal '$ENV' environment with conda packages only..."
  # Create minimal environment with essential packages from conda
  conda create -n "$ENV" python=3.9 pip flask requests numpy pandas scipy scikit-learn nltk spacy transformers pytorch cpuonly -c pytorch -c conda-forge --yes
  if [ $? -ne 0 ]; then
    echo "[WARNING] Failed to create full environment $ENV, creating basic one..."
    conda create -n "$ENV" python=3.9 pip flask requests numpy pandas --yes
    if [ $? -ne 0 ]; then
      echo "[ERROR] Failed to create environment: $ENV"
      exit 1
    fi
  fi

  echo "[SUCCESS] Environment '$ENV' created with conda packages"
done

echo "[GremlinGPT] ✅ All environments created with conda packages (pip requirements skipped due to network issues)"

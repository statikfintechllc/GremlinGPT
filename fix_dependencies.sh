#!/bin/bash

# GremlinGPT Critical Dependencies Fix Script
# This script installs missing dependencies that are causing system failures

echo "🔧 Fixing GremlinGPT Critical Dependencies..."

# Function to install packages in conda environment
install_in_env() {
    local env_name=$1
    local package=$2
    
    echo "Installing $package in $env_name environment..."
    
    if conda activate $env_name 2>/dev/null; then
        pip install $package || conda install $package -y || echo "Warning: Failed to install $package in $env_name"
        conda deactivate
    else
        echo "Warning: Could not activate environment $env_name"
    fi
}

# Ensure conda is available
if ! command -v conda &> /dev/null; then
    echo "Conda not found. Trying to source conda..."
    if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "/usr/share/miniconda/etc/profile.d/conda.sh" ]; then
        source "/usr/share/miniconda/etc/profile.d/conda.sh"
    fi
fi

echo "1. Installing backend dependencies..."
install_in_env "gremlin-dashboard" "flask-socketio"
install_in_env "gremlin-dashboard" "eventlet"
install_in_env "gremlin-dashboard" "loguru"

echo "2. Installing NLP dependencies..."
install_in_env "gremlin-nlp" "loguru"
install_in_env "gremlin-nlp" "transformers"
install_in_env "gremlin-nlp" "torch"

echo "3. Installing orchestrator dependencies..."
install_in_env "gremlin-orchestrator" "loguru"

echo "4. Installing memory dependencies..."
install_in_env "gremlin-memory" "loguru"

echo "5. Installing scraper dependencies..."
install_in_env "gremlin-scraper" "loguru"

echo "6. Setting up offline NLP models..."
# Create cache directory for offline models
mkdir -p data/models/transformers_cache

# Set environment variable for offline mode
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1

echo "✅ Dependencies fix completed!"
echo ""
echo "📝 Summary of changes:"
echo "  - Installed flask-socketio and eventlet for backend"
echo "  - Installed loguru for consistent logging"
echo "  - Set up offline mode for transformers"
echo "  - Created model cache directory"
echo ""
echo "🚀 You can now try running the system again:"
echo "   ./run/start_all.sh"

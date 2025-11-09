# NLTK Setup and Troubleshooting Guide

## Overview

GremlinGPT uses NLTK (Natural Language Toolkit) for text processing across multiple services. This guide explains the NLTK setup process and how to troubleshoot common issues.

## Architecture

### NLTK Data Location
- **Primary**: `$GREMLIN_HOME/data/nltk_data`
- **Environment Variable**: `NLTK_DATA` is set to this path across all environments
- **Centralized Setup**: `utils/nltk_setup.py` manages all NLTK initialization

### Required NLTK Resources
1. **punkt** - Sentence tokenizer
2. **punkt_tab** - Tabular sentence tokenizer (newer NLTK versions)
3. **averaged_perceptron_tagger** - Part-of-speech tagger
4. **wordnet** - Lexical database  
5. **stopwords** - Common stopwords for filtering
6. **omw-1.4** - Open Multilingual Wordnet

## Setup Process

### Automatic Setup (Recommended)

When you run `./run/start_all.sh`, NLTK is automatically configured:

```bash
cd /home/runner/work/GremlinGPT/GremlinGPT
./run/start_all.sh
```

The startup script will:
1. Create the `data/nltk_data` directory
2. Download all required NLTK resources
3. Set the `NLTK_DATA` environment variable
4. Verify permissions and provide fallback if needed

### Manual Setup

If you need to set up NLTK manually:

```python
from utils.nltk_setup import setup_nltk_data

# This will download all required resources
nltk_path = setup_nltk_data()
print(f"NLTK data installed to: {nltk_path}")
```

### Validation

Check if NLTK is properly configured:

```bash
# Run validation script
python run/validate_startup.py

# Or check programmatically
python -c "from utils.nltk_setup import validate_nltk_installation; print(validate_nltk_installation())"
```

## Environment Integration

### Conda Environments

All five GremlinGPT conda environments are configured for NLTK:

1. **gremlin-nlp** - Primary NLP processing
   - Location: `conda_envs/environments/nlp/globals.py`
   - Uses: Full NLTK suite with transformers

2. **gremlin-orchestrator** - Core coordination
   - Location: `conda_envs/environments/orchestrator/globals.py`
   - Uses: Basic NLTK for task processing

3. **gremlin-scraper** - Web scraping
   - Location: `conda_envs/environments/scraper/globals.py`
   - Uses: NLTK for text extraction

4. **gremlin-memory** - Vector storage
   - Location: `conda_envs/environments/memory/globals.py`
   - Uses: NLTK for text preprocessing

5. **gremlin-dashboard** - UI/Visualization
   - Location: `conda_envs/environments/dashboard/globals.py`
   - Uses: NLTK for display formatting

### Import Pattern

All services use consistent NLTK imports:

```python
# Import environment-specific globals (includes NLTK setup)
from conda_envs.environments.nlp.globals import *

# NLTK_DATA is already configured
# HAS_NLTK flag indicates availability
if HAS_NLTK:
    # Use NLTK functionality
    from nltk.tokenize import word_tokenize
else:
    # Graceful degradation
    word_tokenize = lambda text: text.split()
```

## Troubleshooting

### Issue: NLTK Module Not Found

**Symptom:**
```
ModuleNotFoundError: No module named 'nltk'
```

**Solution:**
```bash
# Activate appropriate conda environment
conda activate gremlin-nlp  # or other environment

# Install NLTK
pip install nltk
```

### Issue: NLTK Data Not Found

**Symptom:**
```
LookupError: Resource punkt not found
```

**Solution:**
```bash
# Run setup manually
python -c "from utils.nltk_setup import setup_nltk_data; setup_nltk_data()"

# Or download specific resource
python -c "import nltk; nltk.download('punkt', download_dir='data/nltk_data')"
```

### Issue: Permission Denied

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: 'data/nltk_data'
```

**Solution:**
```bash
# Fix directory permissions
chmod -R u+w data/nltk_data

# Or use fallback directory (automatic in utils/nltk_setup.py)
export NLTK_DATA=/tmp/gremlin_nltk_data
```

### Issue: Services Start Without NLTK

**Symptom:**
Services run but show warnings about NLTK being unavailable.

**Solution:**
This is expected behavior! GremlinGPT is designed to run with graceful degradation:
- Core functionality works without NLTK
- Advanced NLP features are disabled
- Services continue operating with fallback mechanisms

To enable full functionality:
1. Install NLTK in the appropriate conda environment
2. Run `setup_nltk_data()` to download resources
3. Restart the affected services

### Issue: NLTK_DATA Environment Variable Not Set

**Symptom:**
NLTK downloads to `~/nltk_data` instead of project directory.

**Solution:**
```bash
# Set environment variable
export NLTK_DATA="$PWD/data/nltk_data"

# Or add to your shell profile
echo 'export NLTK_DATA="$GREMLIN_HOME/data/nltk_data"' >> ~/.bashrc
```

## Service-Specific NLTK Usage

### NLP Service (nlp_engine/nlp_service.py)
- **Purpose**: Primary NLP processing endpoint
- **NLTK Usage**: Tokenization, POS tagging, sentence splitting
- **Fallback**: Pure Python string operations

### Memory Embedder (memory/vector_store/embedder.py)
- **Purpose**: Text vectorization and storage
- **NLTK Usage**: Text preprocessing, cleaning
- **Fallback**: Basic regex-based cleaning

### Scraper Loop (scraper/scraper_loop.py)
- **Purpose**: Web content extraction
- **NLTK Usage**: Sentence boundary detection
- **Fallback**: Period-based splitting

### Core Loop (core/loop.py)
- **Purpose**: Main orchestration loop
- **NLTK Usage**: Minimal (relies on other services)
- **Fallback**: N/A (delegates to NLP service)

### FSM Agent (agent_core/fsm.py)
- **Purpose**: Task queue management
- **NLTK Usage**: Dataset generation
- **Fallback**: Skip NLP enhancement

## Performance Considerations

### Startup Time
- First run: 2-5 minutes (downloading NLTK resources)
- Subsequent runs: <10 seconds (resources cached)

### Disk Usage
- NLTK resources: ~100-200 MB
- Location: `data/nltk_data/`

### Memory Usage
- Per service: 50-100 MB additional for NLTK models
- Shared across processes via disk caching

## Advanced Configuration

### Custom NLTK Data Path

To use a different NLTK data directory:

```python
import os
os.environ['NLTK_DATA'] = '/custom/path/nltk_data'

from utils.nltk_setup import setup_nltk_data
setup_nltk_data()  # Will use custom path
```

### Minimal NLTK Installation

For resource-constrained environments, install only essential packages:

```python
from utils.nltk_setup import setup_nltk_data
import nltk

# Download only punkt for basic tokenization
nltk.download('punkt', download_dir='data/nltk_data')
```

### Multiple Environments

When running multiple GremlinGPT instances:

```bash
# Instance 1
export NLTK_DATA="/path/to/instance1/data/nltk_data"

# Instance 2  
export NLTK_DATA="/path/to/instance2/data/nltk_data"
```

## Validation Checklist

Before reporting NLTK issues, verify:

- [ ] NLTK is installed: `python -c "import nltk; print(nltk.__version__)"`
- [ ] Data directory exists: `ls -la data/nltk_data`
- [ ] Environment variable set: `echo $NLTK_DATA`
- [ ] Resources downloaded: `python -c "from utils.nltk_setup import validate_nltk_installation; print(validate_nltk_installation())"`
- [ ] Services can import: `python run/validate_startup.py`
- [ ] Permissions correct: `ls -la data/nltk_data/*`

## Support

For NLTK-related issues:

1. **Check logs**: `tail -f data/logs/*/nlp*.log`
2. **Run validation**: `python run/validate_startup.py`
3. **Review this guide**: Common issues covered above
4. **Check NLTK docs**: https://www.nltk.org/
5. **Report bug**: Include output from validation script

## References

- NLTK Documentation: https://www.nltk.org/
- GremlinGPT Architecture: `docs/README.md`
- Environment Setup: `conda_envs/README.md`
- Startup Scripts: `run/start_all.sh`

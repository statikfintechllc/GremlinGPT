# GremlinGPT - Living AI Ecosystem

**Version 1.0.3** - Autonomous AI System with Enhanced Dashboard

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/statikfintechllc/GremlinGPT.git
   cd GremlinGPT
   ```

2. **Run the installation script:**
   ```bash
   ./install.sh
   ```

## Running GremlinGPT

### Option 1: Enhanced Electron Dashboard (Recommended)
Launch the complete GremlinGPT experience with tabbed interface:

```bash
cd frontend
npm run electron
```

The Enhanced Dashboard provides:
- 🎛️ **CLI Dashboard** - Interactive command line interface
- 🧠 **Memory Systems** - Vector stores and embeddings management  
- 🤖 **Agents** - AI agent monitoring and control
- 📝 **Source Editor** - Monaco-based code editor with file tree
- ⚙️ **Settings** - System configuration management

### Option 2: Command Line Interface
Launch the traditional CLI interface:

```bash
python3 utils/enhanced_dash_cli.py
```

### Option 3: System Services Only
Start all backend services without the GUI:

```bash
./run/start_all.sh
```

## System Requirements

- **Python 3.8+** with conda environment support
- **Node.js 16+** (for Electron dashboard)
- **4GB+ RAM** recommended
- **Linux/macOS** (Windows support via WSL)

## Quick Start Guide

1. **Install:** `./install.sh`
2. **Launch:** `cd frontend && npm run electron`
3. **Access the Enhanced CLI Dashboard** (default landing page)
4. **Start the system** using the CLI command: `start`
5. **Monitor status** with: `status`

## Available Commands

In the Enhanced CLI Dashboard:

| Command | Description |
|---------|-------------|
| `start` | Start all GremlinGPT services |
| `stop` | Stop all services |
| `restart` | Restart the system |
| `status` | Show detailed system status |
| `logs` | View recent system logs |
| `agents` | List active AI agents |
| `memory` | Show memory system status |
| `config` | Display configuration |
| `help` | Show available commands |
| `clear` | Clear terminal |

## System Architecture

GremlinGPT runs as a distributed system with multiple specialized components:

- **Core Loop** - Main orchestration engine
- **FSM Agent** - Finite state machine for decision making
- **NLP Service** - Natural language processing
- **Memory Service** - Vector embeddings and knowledge storage
- **Scraper Agent** - Web data collection
- **Self-Trainer** - Continuous learning system
- **Backend API** - REST API services
- **Enhanced Dashboard** - Electron-based GUI

## Ports and Services

Default port allocation (automatically managed):

| Service | Port | Purpose |
|---------|------|---------|
| Backend API | 8000 | REST API endpoints |
| Frontend | 8080 | Web interface |
| NLP Service | 8001 | Language processing |
| Memory Service | 8002 | Vector storage |
| FSM Agent | 8003 | State management |
| Scraper | 8004 | Data collection |
| Trainer | 8005 | Learning system |

## Stopping the System

**From Enhanced CLI Dashboard:**
```
stop
```

**From command line:**
```bash
./run/stop_all.sh
```

## Logs and Monitoring

- **System logs:** `data/logs/`
- **Health monitoring:** Automatic with `start_all.sh`
- **Real-time status:** Available in Enhanced Dashboard
- **Startup summary:** `data/logs/startup_summary.json`

## Development Mode

For development with hot reload:

```bash
cd frontend
npm run electron-dev
```

## Troubleshooting

**Common Issues:**

1. **Port conflicts:** The system automatically detects and resolves port conflicts
2. **Conda environment errors:** Ensure conda is properly installed and initialized
3. **Permission errors:** Make sure install.sh is executable: `chmod +x install.sh`
4. **Memory issues:** Increase system RAM or reduce concurrent processes

**Getting Help:**
- Use `help` command in the Enhanced CLI Dashboard
- Check logs in `data/logs/` directory
- View system status with `status` command

## License

GremlinGPT Dual License v1.0 - Fair Use Only  
Commercial Use Requires License  
© 2025 StatikFintechLLC / AscendAI Project

---

**Quick Commands:**
```bash
# Complete installation and launch
./install.sh && cd frontend && npm run electron

# Check system status
python3 utils/enhanced_dash_cli.py --status

# View logs
tail -f data/logs/*.log
```
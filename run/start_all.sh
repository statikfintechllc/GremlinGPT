#!/usr/bin/env bash

# --- AscendAI GremlinGPT Start Script ---
# This script launches all GremlinGPT subsystems in separate terminal windows.  

# It ensures that the environment is set up correctly and that all necessary services are running.
setopt NO_GLOB_SUBST

# --- Environment Setup ---
# Ensure the script runs in the user's home directory
# and sets up the necessary environment variables.
# This allows for dynamic project paths and log directories.
# It also ensures that the NLTK data directory is created and configured correctly.
# This script should be run from the GremlinGPT project root directory.
# If run from a different directory, it will still work as long as the environment variables are
GREMLIN_HOME="$(pwd)"
PYTHONPATH="$GREMLIN_HOME"
LOGDIR="$GREMLIN_HOME/data/logs"

# --- Dynamic Project Path ---
export GREMLIN_HOME="$GREMLIN_HOME"
export PYTHONPATH="$GREMLIN_HOME"

# --- Log Directory ---
export LOGDIR="$GREMLIN_HOME/data/logs"

# Ensure log directory exists
mkdir -p "$LOGDIR"

# --- Port Management ---
# Define unique ports for each service to avoid conflicts
# Backend uses port from config (8080), frontend uses Astro dev server (4321)
declare -A SERVICE_PORTS=(
  ["backend"]="8080"
  ["frontend"]="4321"
  ["nlp"]="8001"
  ["memory"]="8002"
  ["fsm"]="8003"
  ["scraper"]="8004"
  ["trainer"]="8005"
  ["ngrok"]="8006"
)

# --- Port Conflict Detection ---
function check_port_conflicts() {
  echo "[PORTS] Checking for port conflicts..."
  local conflicts=()
  
  for service in "${!SERVICE_PORTS[@]}"; do
    local port="${SERVICE_PORTS[$service]}"
    if lsof -i :$port >/dev/null 2>&1; then
      conflicts+=("$service:$port")
      echo "[PORTS] WARNING: Port $port already in use (service: $service)"
    fi
  done
  
  if [ ${#conflicts[@]} -gt 0 ]; then
    echo "[PORTS] Port conflicts detected: ${conflicts[*]}"
    echo "[PORTS] Attempting to resolve conflicts..."
    
    for conflict in "${conflicts[@]}"; do
      local service=$(echo $conflict | cut -d: -f1)
      local port=$(echo $conflict | cut -d: -f2)
      
      # Try to find alternative port
      local new_port=$((port + 100))
      while lsof -i :$new_port >/dev/null 2>&1; do
        new_port=$((new_port + 1))
      done
      
      SERVICE_PORTS[$service]=$new_port
      echo "[PORTS] Reassigned $service from $port to $new_port"
    done
  fi
  
  echo "[PORTS] Final port allocation:"
  for service in "${!SERVICE_PORTS[@]}"; do
    echo "[PORTS]   $service: ${SERVICE_PORTS[$service]}"
  done
}

# --- Process Health Monitoring ---
declare -A SERVICE_PIDS=()

function start_health_monitor() {
  echo "[HEALTH] Starting system health monitor..."
  
  # Create monitoring script
  cat > "/tmp/gremlin_health_monitor.sh" << 'EOF'
#!/bin/bash
GREMLIN_HOME="$1"
LOGDIR="$GREMLIN_HOME/data/logs"
MONITOR_LOG="$LOGDIR/health_monitor.log"

echo "[$(date)] Health monitor started" >> "$MONITOR_LOG"

while true; do
  sleep 60  # Check every minute
  
  # Check all service PIDs
  dead_services=()
  
  for pidfile in /tmp/gremlin_*.pid; do
    if [ -f "$pidfile" ]; then
      service_name=$(basename "$pidfile" .pid | sed 's/gremlin_//')
      pid=$(cat "$pidfile")
      
      if ! kill -0 "$pid" 2>/dev/null; then
        dead_services+=("$service_name")
        echo "[$(date)] Service died: $service_name (PID: $pid)" >> "$MONITOR_LOG"
        rm -f "$pidfile"
      fi
    fi
  done
  
  # Log health status
  active_services=$(ls /tmp/gremlin_*.pid 2>/dev/null | wc -l)
  echo "[$(date)] Health check: $active_services services active" >> "$MONITOR_LOG"
  
  # Calculate health score
  total_expected=8
  health_score=$((active_services * 100 / total_expected))
  echo "[$(date)] System health score: $health_score%" >> "$MONITOR_LOG"
  
  # Alert if health is degraded
  if [ $health_score -lt 75 ]; then
    echo "[$(date)] WARNING: System health degraded ($health_score%)" >> "$MONITOR_LOG"
    if [ ${#dead_services[@]} -gt 0 ]; then
      echo "[$(date)] Dead services: ${dead_services[*]}" >> "$MONITOR_LOG"
    fi
  fi
done
EOF
  
  chmod +x "/tmp/gremlin_health_monitor.sh"
  nohup "/tmp/gremlin_health_monitor.sh" "$GREMLIN_HOME" &
  MONITOR_PID=$!
  echo $MONITOR_PID > "/tmp/gremlin_health_monitor.pid"
  echo "[HEALTH] Health monitor started with PID: $MONITOR_PID"
}

function validate_startup() {
  echo "[VALIDATION] Running startup validation tests..."
  
  # Test 1: Check if all expected services started
  local expected_services=("Core_Loop" "NLP_Service" "Memory_Service" "FSM_Agent" "Scraper" "Self-Trainer" "Backend_Server" "Frontend")
  local started_services=0
  
  for service in "${expected_services[@]}"; do
    local pidfile="/tmp/gremlin_${service// /_}.pid"
    if [ -f "$pidfile" ]; then
      local pid=$(cat "$pidfile")
      if kill -0 "$pid" 2>/dev/null; then
        echo "[VALIDATION] ✓ $service is running (PID: $pid)"
        started_services=$((started_services + 1))
      else
        echo "[VALIDATION] ✗ $service failed to start"
      fi
    else
      echo "[VALIDATION] ✗ $service PID file not found"
    fi
  done
  
  # Test 2: Port accessibility
  echo "[VALIDATION] Testing service ports..."
  local accessible_ports=0
  for service in "${!SERVICE_PORTS[@]}"; do
    local port="${SERVICE_PORTS[$service]}"
    if nc -z localhost $port 2>/dev/null; then
      echo "[VALIDATION] ✓ Port $port ($service) is accessible"
      accessible_ports=$((accessible_ports + 1))
    else
      echo "[VALIDATION] ✗ Port $port ($service) is not accessible"
    fi
  done
  
  # Test 3: Log file creation
  echo "[VALIDATION] Checking log files..."
  local log_files_created=0
  for logfile in "$LOGDIR"/*.log "$LOGDIR"/*.out; do
    if [ -f "$logfile" ] && [ -s "$logfile" ]; then
      log_files_created=$((log_files_created + 1))
    fi
  done
  
  # Calculate overall health score
  local total_checks=$((${#expected_services[@]} + ${#SERVICE_PORTS[@]} + 1))
  local passed_checks=$((started_services + accessible_ports + (log_files_created > 0 ? 1 : 0)))
  local health_score=$((passed_checks * 100 / total_checks))
  
  echo "[VALIDATION] === Startup Validation Results ==="
  echo "[VALIDATION] Services Started: $started_services/${#expected_services[@]}"
  echo "[VALIDATION] Ports Accessible: $accessible_ports/${#SERVICE_PORTS[@]}"
  echo "[VALIDATION] Log Files: $log_files_created"
  echo "[VALIDATION] Overall Health Score: $health_score%"
  
  if [ $health_score -ge 75 ]; then
    echo "[VALIDATION] ✅ System startup SUCCESSFUL"
    return 0
  else
    echo "[VALIDATION] ⚠️ System startup DEGRADED"
    return 1
  fi
}

# --- NLTK Bootstrap: Always under repo, not home! ---
python3 - <<'EOF'
import os, nltk
nltk_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data/nltk_data"))
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)
for pkg, path in [
    ("punkt", "tokenizers/punkt"),
    ("averaged_perceptron_tagger", "taggers/averaged_perceptron_tagger"),
    ("wordnet", "corpora/wordnet"),
    ("stopwords", "corpora/stopwords"),
]:
    try: nltk.data.find(path)
    except LookupError: nltk.download(pkg, download_dir=nltk_data_dir)
EOF

# --- Terminal detection ---
TERM_EMU=$(command -v gnome-terminal || command -v xterm)

function launch_terminal() {
  local title="$1"
  local env="$2"
  local cmd="$3"
  local logfile="$4"
  local port="${5:-}"

  echo "[LAUNCH] Starting $title in background with env $env..."
  
  # Update command to use assigned port if applicable
  if [ -n "$port" ] && [[ "$cmd" == *"server"* ]]; then
    cmd="${cmd} --port $port"
  elif [ -n "$port" ] && [[ "$cmd" == *"http.server"* ]]; then
    cmd="${cmd/$port}"  # Replace existing port
    cmd="$cmd $port"
    cmd="${cmd} --port $port"
  elif [ -n "$port" ] && [[ "$cmd" == *"nlp_service"* ]]; then
    cmd="${cmd} --port $port"
  fi
  
  # Check if we're in a headless environment or GUI environment
  if [ -z "$DISPLAY" ] || ! command -v gnome-terminal > /dev/null; then
    echo "[HEADLESS] Running $title as background process"
    
    # Run in background with proper conda environment
    (
      # Try multiple conda locations
      if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source $HOME/miniconda3/etc/profile.d/conda.sh
      elif [ -f "/usr/share/miniconda/etc/profile.d/conda.sh" ]; then
        source /usr/share/miniconda/etc/profile.d/conda.sh
      elif [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
        source /opt/conda/etc/profile.d/conda.sh
      else
        echo "[$title] Warning: Could not find conda.sh, using base Python environment"
      fi
      
      conda activate $env 2>/dev/null || { echo "[$title] Warning: Failed to activate env: $env, using base environment"; }
      export NLTK_DATA="$GREMLIN_HOME/data/nltk_data"
      export PYTHONPATH="$GREMLIN_HOME:$PYTHONPATH"
      echo "[$title] ENV: ${CONDA_DEFAULT_ENV:-base}" | tee -a $logfile
      echo "[$title] CWD: $PWD" | tee -a $logfile
      echo "[$title] PYTHONPATH: $PYTHONPATH" | tee -a $logfile
      echo "[$title] Running: $cmd" | tee -a $logfile
      if [ -n "$port" ]; then
        echo "[$title] Port: $port" | tee -a $logfile
      fi
      cd "$GREMLIN_HOME"
      eval $cmd 2>&1 | tee -a $logfile &
      PID=$!
      echo "[$title] Started with PID: $PID" | tee -a $logfile
      echo $PID > "/tmp/gremlin_${title// /_}.pid"
      wait $PID
      EXIT_CODE=$?
      echo "[$title] Process exited with code $EXIT_CODE" | tee -a $logfile
    ) &
    sleep 1
  else
    # Original GUI terminal launch code
    local preamble="
      source \$HOME/miniconda3/etc/profile.d/conda.sh
      conda activate $env || { echo '[${title}] Failed to activate env: $env'; exec zsh; }
      export NLTK_DATA=\"\$GREMLIN_HOME/data/nltk_data\"
      echo '[${title}] ENV:' \$CONDA_DEFAULT_ENV
      echo '[${title}] CWD:' \$PWD
      echo '[${title}] Running: $cmd'
      $cmd | tee $logfile
      EXIT_CODE=\${PIPESTATUS[0]}
      echo '[${title}] Process exited with code' \$EXIT_CODE
      exec zsh
    "

    if command -v gnome-terminal > /dev/null; then
      gnome-terminal --title="$title" -- zsh --login -c "$preamble"
    elif command -v xterm > /dev/null; then
      xterm -T "$title" -e "zsh --login -c '$preamble'"
    else
      echo "No supported terminal emulator found (gnome-terminal or xterm)."
      exit 1
    fi
  fi
}

echo "[BOOT] Injecting GremlinGPT watermark to system trace."
echo "Boot ID: $(uuidgen) | Source: GremlinGPT | Time: $(date -u)" | tee -a "$LOGDIR/gremlin_boot_trace.log"

# --- Pre-launch Setup ---
check_port_conflicts

echo "[START] Launching GremlinGPT subsystems in dependency order..."
echo "[START] Phase 1: Memory Environment (foundational data layer)"
launch_terminal "Memory Service" gremlin-memory "python memory/vector_store/embedder.py" "$LOGDIR/memory.out" "${SERVICE_PORTS[memory]}"

echo "[START] Waiting for memory service to initialize..."
sleep 5

echo "[START] Phase 2: NLP Environment (language processing)"
launch_terminal "NLP Service" gremlin-nlp "python -m nlp_engine.nlp_service" "$LOGDIR/nlp.out" "${SERVICE_PORTS[nlp]}"
launch_terminal "Self-Trainer" gremlin-nlp "python -m self_training.trainer" "$LOGDIR/trainer.out" "${SERVICE_PORTS[trainer]}"

echo "[START] Waiting for NLP services to initialize..."
sleep 5

echo "[START] Phase 3: Scraper Environment (data collection)"
launch_terminal "Scraper" gremlin-scraper "python -m scraper.scraper_loop" "$LOGDIR/scraper.out" "${SERVICE_PORTS[scraper]}"

echo "[START] Waiting for scraper to initialize..."
sleep 3

echo "[START] Phase 4: Orchestrator Environment (coordination & agents)"
launch_terminal "Core Loop" gremlin-orchestrator "python core/loop.py" "$LOGDIR/runtime.log"
launch_terminal "FSM Agent" gremlin-orchestrator "python -m agent_core.fsm" "$LOGDIR/fsm.out" "${SERVICE_PORTS[fsm]}"
launch_terminal "Backend Server" gremlin-orchestrator "python -m backend.server" "$LOGDIR/backend.out" "${SERVICE_PORTS[backend]}"

echo "[START] Waiting for orchestrator services to initialize..."
sleep 5

echo "[START] Phase 5: Dashboard Environment (UI & visualization)"
launch_terminal "Frontend" gremlin-dashboard "cd frontend && npm run dev" "$LOGDIR/frontend.out" "${SERVICE_PORTS[frontend]}"
launch_terminal "Ngrok Tunnel" gremlin-dashboard "python run/ngrok_launcher.py" "$LOGDIR/ngrok.out" "${SERVICE_PORTS[ngrok]}"

# --- Wait for services to initialize ---
echo "[STARTUP] Waiting for services to initialize..."
sleep 10

# --- Start health monitoring ---
start_health_monitor

# --- Run startup validation ---
validate_startup
VALIDATION_RESULT=$?

# --- Playwright install check for scraper (headless) ---
if [ -f "/usr/share/miniconda/etc/profile.d/conda.sh" ]; then
  source /usr/share/miniconda/etc/profile.d/conda.sh
  conda activate gremlin-scraper 2>/dev/null || echo "[INFO] Could not activate gremlin-scraper environment"
  python -c "import playwright; print('Playwright OK')" 2>/dev/null || echo "[INFO] Playwright not available, install with: pip install playwright && playwright install"
  conda deactivate 2>/dev/null || true
fi

# --- Ngrok CLI check ---
if ! command -v ngrok &> /dev/null; then
    echo "[NOTICE] ngrok not found. Visit https://ngrok.com/download or configure pyngrok in config.toml"
else
    echo "[INFO] ngrok installed: $(which ngrok)"
fi

# --- Final Status Report ---
echo "═══════════════════════════════════════════"
echo "🧠 GremlinGPT System Startup Complete"
echo "═══════════════════════════════════════════"
echo "Backend:     http://localhost:${SERVICE_PORTS[backend]}"
echo "Frontend:    http://localhost:${SERVICE_PORTS[frontend]}"
echo "Logs:        $GREMLIN_HOME/data/logs/"
echo "Health:      $([ $VALIDATION_RESULT -eq 0 ] && echo "✅ Healthy" || echo "⚠️ Degraded")"
echo "Monitor:     Health monitoring active"
echo ""
echo "Port Allocation:"
for service in "${!SERVICE_PORTS[@]}"; do
  echo "  $service: ${SERVICE_PORTS[$service]}"
done
echo "═══════════════════════════════════════════"

# --- Dashboard Launch Info ---
if [ -d "$GREMLIN_HOME/frontend" ] && [ -f "$GREMLIN_HOME/frontend/package.json" ]; then
  echo "Detected Electron frontend. To launch Enhanced Dashboard:"
  echo "  cd frontend && npm run electron"
  echo ""
  echo "For development with hot reload:"
  echo "  cd frontend && npm run electron-dev"
fi

# --- Create summary file ---
cat > "$LOGDIR/startup_summary.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "validation_result": $VALIDATION_RESULT,
  "service_ports": $(printf '{'; for service in "${!SERVICE_PORTS[@]}"; do printf '"'$service'":"'${SERVICE_PORTS[$service]}'"'; done | sed 's/}{/,/g'; printf '}'),
  "health_monitor_pid": $(cat /tmp/gremlin_health_monitor.pid 2>/dev/null || echo "null"),
  "log_directory": "$LOGDIR"
}
EOF

echo "[STARTUP] Summary saved to: $LOGDIR/startup_summary.json"

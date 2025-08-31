#!/bin/bash

echo "[STOP] Terminating all GremlinGPT processes..."

# Kill by PID files first
for pidfile in /tmp/gremlin_*.pid; do
  if [ -f "$pidfile" ]; then
    service_name=$(basename "$pidfile" .pid | sed 's/gremlin_//')
    pid=$(cat "$pidfile")
    
    if kill -0 "$pid" 2>/dev/null; then
      echo "[STOP] Terminating $service_name (PID: $pid)"
      kill -TERM "$pid" 2>/dev/null
      sleep 2
      
      # Force kill if still running
      if kill -0 "$pid" 2>/dev/null; then
        echo "[STOP] Force killing $service_name (PID: $pid)"
        kill -KILL "$pid" 2>/dev/null
      fi
    fi
    
    rm -f "$pidfile"
  fi
done

# Comprehensive process termination
echo "[STOP] Killing processes by pattern..."

# Core services
pkill -f "core/loop.py" 2>/dev/null
pkill -f "nlp_engine/nlp_check.py" 2>/dev/null  
pkill -f "memory/vector_store/embedder.py" 2>/dev/null
pkill -f "backend/server" 2>/dev/null
pkill -f "backend.server" 2>/dev/null
pkill -f "agent_core/fsm" 2>/dev/null
pkill -f "scraper/scraper_loop" 2>/dev/null
pkill -f "scraper.scraper_loop" 2>/dev/null
pkill -f "self_training/trainer" 2>/dev/null
pkill -f "self_training.trainer" 2>/dev/null
pkill -f "ngrok_launcher.py" 2>/dev/null

# Frontend services
pkill -f "http.server.*frontend" 2>/dev/null
pkill -f "astro dev" 2>/dev/null
pkill -f "npm.*dev" 2>/dev/null

# Health monitor
pkill -f "gremlin_health_monitor" 2>/dev/null

# Any remaining Python processes with gremlin in path
pkill -f "python.*gremlin" 2>/dev/null

echo "[STOP] Waiting for processes to terminate..."
sleep 3

# Final cleanup of any remaining processes
ps aux | grep -E "(gremlin|backend\.server|astro.*dev)" | grep -v grep | awk '{print $2}' | xargs -r kill -9 2>/dev/null

# Clean up temporary files
rm -f /tmp/gremlin_*.pid
rm -f /tmp/gremlin_health_monitor.sh

echo "[STOP] All GremlinGPT subsystems stopped."


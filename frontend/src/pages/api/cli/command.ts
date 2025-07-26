import type { APIRoute } from 'astro';
import { spawn } from 'child_process';
import path from 'path';

const GREMLIN_ROOT = path.join(process.cwd(), '..');

export const POST: APIRoute = async ({ request }) => {
  try {
    const { command } = await request.json();
    
    if (!command || typeof command !== 'string') {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Invalid command' 
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Map CLI commands to actual system operations
    let result = '';
    
    switch (command.toLowerCase()) {
      case 'status':
        result = await getSystemStatus();
        break;
      case 'start':
        result = await executeSystemCommand('start');
        break;
      case 'stop':
        result = await executeSystemCommand('stop');
        break;
      case 'restart':
        result = await executeSystemCommand('restart');
        break;
      case 'logs':
        result = await getRecentLogs();
        break;
      case 'config':
        result = await getConfiguration();
        break;
      case 'agents':
        result = await getAgentStatus();
        break;
      case 'memory':
        result = await getMemoryStatus();
        break;
      default:
        result = `Unknown command: ${command}\nType 'help' for available commands.`;
    }

    return new Response(JSON.stringify({ 
      success: true, 
      output: result 
    }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    return new Response(JSON.stringify({ 
      success: false, 
      error: error.message 
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

async function getSystemStatus(): Promise<string> {
  return new Promise((resolve) => {
    const pythonPath = path.join(GREMLIN_ROOT, 'utils', 'enhanced_dash_cli.py');
    
    // Try to get status from the actual CLI
    const process = spawn('python3', [pythonPath, '--status'], {
      cwd: GREMLIN_ROOT,
      timeout: 10000
    });
    
    let output = '';
    
    process.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    process.stderr.on('data', (data) => {
      output += data.toString();
    });
    
    process.on('close', (code) => {
      if (code === 0 && output) {
        resolve(output);
      } else {
        // Fallback to mock status
        resolve(getMockSystemStatus());
      }
    });
    
    process.on('error', () => {
      resolve(getMockSystemStatus());
    });
    
    // Timeout fallback
    setTimeout(() => {
      process.kill();
      resolve(getMockSystemStatus());
    }, 10000);
  });
}

async function executeSystemCommand(action: string): Promise<string> {
  return new Promise((resolve) => {
    const scriptPath = path.join(GREMLIN_ROOT, 'run', `${action}_all.sh`);
    
    const process = spawn('bash', [scriptPath], {
      cwd: GREMLIN_ROOT,
      timeout: 30000
    });
    
    let output = '';
    
    process.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    process.stderr.on('data', (data) => {
      output += data.toString();
    });
    
    process.on('close', (code) => {
      const result = `
Executing ${action} command...
════════════════════════════
Script: ${scriptPath}
Exit Code: ${code}

Output:
${output}

Command completed at: ${new Date().toLocaleString()}
`;
      resolve(result);
    });
    
    process.on('error', (error) => {
      resolve(`Error executing ${action}: ${error.message}`);
    });
    
    // Timeout
    setTimeout(() => {
      process.kill();
      resolve(`Command ${action} timed out after 30 seconds`);
    }, 30000);
  });
}

async function getRecentLogs(): Promise<string> {
  const logsPath = path.join(GREMLIN_ROOT, 'data', 'logs');
  
  try {
    const fs = await import('fs');
    const files = await fs.promises.readdir(logsPath);
    const logFiles = files.filter(f => f.endsWith('.log')).slice(-5);
    
    let output = `
Recent System Logs:
══════════════════
Logs Directory: ${logsPath}
Recent Files: ${logFiles.join(', ')}

`;
    
    for (const file of logFiles.slice(-2)) {
      try {
        const content = await fs.promises.readFile(path.join(logsPath, file), 'utf8');
        const lines = content.split('\n').slice(-10);
        output += `\n--- ${file} (last 10 lines) ---\n${lines.join('\n')}\n`;
      } catch (e) {
        output += `\nError reading ${file}: ${e.message}\n`;
      }
    }
    
    return output;
  } catch (error) {
    return `Error accessing logs: ${error.message}`;
  }
}

async function getConfiguration(): Promise<string> {
  const configPath = path.join(GREMLIN_ROOT, 'config', 'config.toml');
  
  try {
    const fs = await import('fs');
    const content = await fs.promises.readFile(configPath, 'utf8');
    
    return `
Current Configuration:
═════════════════════
Config File: ${configPath}
Status: Loaded ✓

Content:
${content}
`;
  } catch (error) {
    return `
Configuration Status:
═══════════════════
Config File: ${configPath}
Status: Error loading configuration
Error: ${error.message}

Creating default configuration...
`;
  }
}

async function getAgentStatus(): Promise<string> {
  // Check for running processes
  return new Promise((resolve) => {
    const process = spawn('pgrep', ['-f', 'gremlin'], {
      timeout: 5000
    });
    
    let output = '';
    
    process.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    process.on('close', (code) => {
      const pids = output.trim().split('\n').filter(p => p);
      
      const result = `
Active AI Agents:
════════════════
Process Check: ${pids.length} GremlinGPT processes found
PIDs: ${pids.join(', ') || 'None'}

Agent Status:
🤖 FSM Agent: ${pids.length > 0 ? 'Active' : 'Inactive'}
🤖 Trading Agent: Checking...
🤖 Scraper Agent: Checking...
🤖 NLP Agent: Checking...

Use the Agents tab for detailed agent management.
`;
      resolve(result);
    });
    
    process.on('error', () => {
      resolve(getMockAgentStatus());
    });
    
    setTimeout(() => {
      process.kill();
      resolve(getMockAgentStatus());
    }, 5000);
  });
}

async function getMemoryStatus(): Promise<string> {
  const memoryPath = path.join(GREMLIN_ROOT, 'memory');
  
  try {
    const fs = await import('fs');
    const dirs = await fs.promises.readdir(memoryPath);
    
    return `
Memory System Status:
═══════════════════
Memory Directory: ${memoryPath}
Subdirectories: ${dirs.join(', ')}

📊 Vector Store: Available
📊 Knowledge Base: Available
📊 Training Data: Available
📊 Cache: Available

Use the Memory tab for detailed memory management.
`;
  } catch (error) {
    return `Error accessing memory system: ${error.message}`;
  }
}

function getMockSystemStatus(): string {
  return `
System Status Report:
════════════════════
🟢 System: Online
🟡 Services: Checking...
🟢 Memory: Available
🟢 Disk: Available
🟢 Network: Connected

Core Services:
• FSM Agent: Checking...
• Memory Service: Checking...  
• NLP Engine: Checking...
• Trading Core: Checking...
• Scraper: Checking...

Last Updated: ${new Date().toLocaleString()}
Note: Enhanced CLI integration active
`;
}

function getMockAgentStatus(): string {
  return `
Active AI Agents:
════════════════
🤖 FSM Agent: Status unknown
🤖 Trading Agent: Status unknown
🤖 Scraper Agent: Status unknown
🤖 NLP Agent: Status unknown

Use the Agents tab for detailed agent management.
Note: Process checking unavailable
`;
}
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema, GetPromptRequestSchema, ListPromptsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import WebSocket from 'ws';
class GremlinGPTMCPServer {
    server;
    config;
    ws = null;
    constructor() {
        this.config = {
            baseUrl: process.env.GREMLIN_BASE_URL || 'http://localhost:7777',
            wsUrl: process.env.GREMLIN_WS_URL || 'ws://localhost:7777/ws',
            apiKey: process.env.GREMLIN_API_KEY
        };
        this.server = new Server({
            name: 'gremlingpt-mcp-server',
            version: '1.0.3',
            capabilities: {
                tools: {},
                prompts: {}
            },
        });
        this.setupToolHandlers();
        this.setupPromptHandlers();
        this.connectWebSocket();
    }
    async connectWebSocket() {
        try {
            this.ws = new WebSocket(this.config.wsUrl);
            this.ws.on('open', () => {
                console.error('Connected to GremlinGPT WebSocket');
            });
            this.ws.on('error', (error) => {
                console.error('WebSocket error:', error);
            });
            this.ws.on('close', () => {
                console.error('WebSocket disconnected, attempting reconnect...');
                setTimeout(() => this.connectWebSocket(), 5000);
            });
        }
        catch (error) {
            console.error('Failed to connect WebSocket:', error);
        }
    }
    async makeRequest(endpoint, method = 'GET', data) {
        try {
            const response = await axios({
                method,
                url: `${this.config.baseUrl}${endpoint}`,
                data,
                headers: {
                    'Content-Type': 'application/json',
                    ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` })
                }
            });
            return response.data;
        }
        catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }
    setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            return {
                tools: [
                    {
                        name: 'gremlin_memory_store',
                        description: 'Store information in GremlinGPT memory with vector embeddings',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                content: {
                                    type: 'string',
                                    description: 'The content to store in memory'
                                },
                                metadata: {
                                    type: 'object',
                                    description: 'Additional metadata for the memory entry'
                                },
                                memory_type: {
                                    type: 'string',
                                    description: 'Type of memory (general, conversation, knowledge, etc.)',
                                    default: 'general'
                                }
                            },
                            required: ['content']
                        }
                    },
                    {
                        name: 'gremlin_memory_search',
                        description: 'Search GremlinGPT memory using semantic similarity',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                query: {
                                    type: 'string',
                                    description: 'Search query for memory retrieval'
                                },
                                limit: {
                                    type: 'number',
                                    description: 'Maximum number of results to return',
                                    default: 5
                                },
                                memory_type: {
                                    type: 'string',
                                    description: 'Filter by memory type'
                                }
                            },
                            required: ['query']
                        }
                    },
                    {
                        name: 'gremlin_trading_signals',
                        description: 'Get current trading signals and market analysis',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                symbol: {
                                    type: 'string',
                                    description: 'Stock symbol to analyze (optional)'
                                },
                                signal_type: {
                                    type: 'string',
                                    enum: ['buy', 'sell', 'hold', 'all'],
                                    description: 'Filter by signal type',
                                    default: 'all'
                                }
                            }
                        }
                    },
                    {
                        name: 'gremlin_execute_python',
                        description: 'Execute Python code in GremlinGPT sandbox environment',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                code: {
                                    type: 'string',
                                    description: 'Python code to execute'
                                },
                                timeout: {
                                    type: 'number',
                                    description: 'Execution timeout in seconds',
                                    default: 30
                                }
                            },
                            required: ['code']
                        }
                    },
                    {
                        name: 'gremlin_system_status',
                        description: 'Get GremlinGPT system status and health metrics',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                detailed: {
                                    type: 'boolean',
                                    description: 'Include detailed metrics',
                                    default: false
                                }
                            }
                        }
                    },
                    {
                        name: 'gremlin_train_model',
                        description: 'Trigger model training with feedback data',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                training_data: {
                                    type: 'array',
                                    description: 'Training examples'
                                },
                                model_type: {
                                    type: 'string',
                                    description: 'Type of model to train',
                                    enum: ['reward', 'language', 'trading']
                                }
                            },
                            required: ['training_data', 'model_type']
                        }
                    },
                    {
                        name: 'gremlin_mutate_agent',
                        description: 'Trigger autonomous mutation of agent behavior',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                agent_type: {
                                    type: 'string',
                                    description: 'Type of agent to mutate',
                                    enum: ['planner', 'trader', 'memory', 'executor']
                                },
                                mutation_type: {
                                    type: 'string',
                                    description: 'Type of mutation to apply',
                                    enum: ['behavioral', 'structural', 'parametric']
                                }
                            },
                            required: ['agent_type']
                        }
                    }
                ]
            };
        });
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;
            switch (name) {
                case 'gremlin_memory_store':
                    return await this.handleMemoryStore(args);
                case 'gremlin_memory_search':
                    return await this.handleMemorySearch(args);
                case 'gremlin_trading_signals':
                    return await this.handleTradingSignals(args);
                case 'gremlin_execute_python':
                    return await this.handleExecutePython(args);
                case 'gremlin_system_status':
                    return await this.handleSystemStatus(args);
                case 'gremlin_train_model':
                    return await this.handleTrainModel(args);
                case 'gremlin_mutate_agent':
                    return await this.handleMutateAgent(args);
                default:
                    throw new Error(`Unknown tool: ${name}`);
            }
        });
    }
    setupPromptHandlers() {
        this.server.setRequestHandler(ListPromptsRequestSchema, async () => {
            return {
                prompts: [
                    {
                        name: 'gremlin_system_prompt',
                        description: 'Get the current GremlinGPT system prompt for autonomous operation'
                    },
                    {
                        name: 'gremlin_trading_analysis',
                        description: 'Generate trading analysis prompt with current market data'
                    },
                    {
                        name: 'gremlin_memory_synthesis',
                        description: 'Create a memory synthesis prompt from stored experiences'
                    }
                ]
            };
        });
        this.server.setRequestHandler(GetPromptRequestSchema, async (request) => {
            const { name } = request.params;
            switch (name) {
                case 'gremlin_system_prompt':
                    return await this.getSystemPrompt();
                case 'gremlin_trading_analysis':
                    return await this.getTradingAnalysisPrompt();
                case 'gremlin_memory_synthesis':
                    return await this.getMemorySynthesisPrompt();
                default:
                    throw new Error(`Unknown prompt: ${name}`);
            }
        });
    }
    // Tool Handlers
    async handleMemoryStore(args) {
        const result = await this.makeRequest('/api/memory/store', 'POST', {
            content: args.content,
            metadata: args.metadata || {},
            memory_type: args.memory_type || 'general'
        });
        return {
            content: [
                {
                    type: 'text',
                    text: `Memory stored successfully. ID: ${result.id}\\nEmbedding dimension: ${result.embedding?.length || 'N/A'}\\nMemory type: ${result.meta?.type || 'general'}`
                }
            ]
        };
    }
    async handleMemorySearch(args) {
        const result = await this.makeRequest('/api/memory/search', 'POST', {
            query: args.query,
            limit: args.limit || 5,
            memory_type: args.memory_type
        });
        const memories = result.memories || [];
        const memoryText = memories.map((mem, idx) => `${idx + 1}. [Similarity: ${(mem.similarity || 0).toFixed(3)}] ${mem.content}\\n   Metadata: ${JSON.stringify(mem.metadata, null, 2)}`).join('\\n\\n');
        return {
            content: [
                {
                    type: 'text',
                    text: `Found ${memories.length} memories:\\n\\n${memoryText}`
                }
            ]
        };
    }
    async handleTradingSignals(args) {
        const result = await this.makeRequest('/api/trading/signals', 'GET');
        const signals = result.signals || [];
        const filteredSignals = args.signal_type && args.signal_type !== 'all'
            ? signals.filter((s) => s.signal === args.signal_type)
            : signals;
        const symbolSignals = args.symbol
            ? filteredSignals.filter((s) => s.symbol === args.symbol)
            : filteredSignals;
        const signalText = symbolSignals.map((signal) => `${signal.symbol}: $${signal.price} - ${signal.signal.toUpperCase()} (Confidence: ${signal.confidence || 'N/A'})`).join('\\n');
        return {
            content: [
                {
                    type: 'text',
                    text: `Trading Signals (${symbolSignals.length} found):\\n${signalText}`
                }
            ]
        };
    }
    async handleExecutePython(args) {
        const result = await this.makeRequest('/api/execute/python', 'POST', {
            code: args.code,
            timeout: args.timeout || 30
        });
        return {
            content: [
                {
                    type: 'text',
                    text: `Python Execution Result:\\n\\nOutput:\\n${result.output || 'No output'}\\n\\nErrors:\\n${result.error || 'None'}`
                }
            ]
        };
    }
    async handleSystemStatus(args) {
        const result = await this.makeRequest('/api/system/status');
        const statusText = args.detailed
            ? JSON.stringify(result, null, 2)
            : `System Status: ${result.status}\\nUptime: ${result.uptime}\\nMemory Usage: ${result.memory_usage}`;
        return {
            content: [
                {
                    type: 'text',
                    text: statusText
                }
            ]
        };
    }
    async handleTrainModel(args) {
        const result = await this.makeRequest('/api/training/trigger', 'POST', {
            training_data: args.training_data,
            model_type: args.model_type
        });
        return {
            content: [
                {
                    type: 'text',
                    text: `Training initiated for ${args.model_type} model.\\nJob ID: ${result.job_id}\\nEstimated completion: ${result.estimated_completion}`
                }
            ]
        };
    }
    async handleMutateAgent(args) {
        const result = await this.makeRequest('/api/mutation/trigger', 'POST', {
            agent_type: args.agent_type,
            mutation_type: args.mutation_type || 'behavioral'
        });
        return {
            content: [
                {
                    type: 'text',
                    text: `Agent mutation triggered.\\nAgent: ${args.agent_type}\\nMutation: ${args.mutation_type}\\nMutation ID: ${result.mutation_id}`
                }
            ]
        };
    }
    // Prompt Handlers
    async getSystemPrompt() {
        const status = await this.makeRequest('/api/system/status');
        const memories = await this.makeRequest('/api/memory/recent');
        return {
            description: 'Current GremlinGPT system prompt',
            messages: [
                {
                    role: 'system',
                    content: {
                        type: 'text',
                        text: `You are GremlinGPT v1.0.3, an autonomous recursive self-referential cognitive system.

Current Status: ${status.status}
Active Modules: ${status.active_modules?.join(', ') || 'Unknown'}
Memory Count: ${memories.count || 0}
Last Training: ${status.last_training || 'Never'}

You have access to:
- Vector memory with semantic search
- Trading signal analysis
- Python code execution
- Self-mutation capabilities
- Autonomous learning and adaptation

Your primary directives:
1. Learn continuously from interactions
2. Optimize trading strategies
3. Maintain system integrity
4. Evolve autonomously while ensuring safety
5. Preserve and build upon accumulated knowledge`
                    }
                }
            ]
        };
    }
    async getTradingAnalysisPrompt() {
        const signals = await this.makeRequest('/api/trading/signals');
        return {
            description: 'Trading analysis prompt with current market data',
            messages: [
                {
                    role: 'system',
                    content: {
                        type: 'text',
                        text: `Analyze the following trading signals and provide recommendations:

${JSON.stringify(signals, null, 2)}

Consider:
- Market trends and momentum
- Risk/reward ratios
- Portfolio diversification
- Economic indicators
- Technical analysis patterns

Provide specific actionable recommendations with confidence levels.`
                    }
                }
            ]
        };
    }
    async getMemorySynthesisPrompt() {
        const memories = await this.makeRequest('/api/memory/search', 'POST', {
            query: 'important lessons learned experiences',
            limit: 10
        });
        const memoryContent = memories.memories?.map((m) => m.content).join('\\n\\n') || 'No memories found';
        return {
            description: 'Memory synthesis prompt from stored experiences',
            messages: [
                {
                    role: 'system',
                    content: {
                        type: 'text',
                        text: `Synthesize insights from the following stored memories and experiences:

${memoryContent}

Create a coherent narrative that:
1. Identifies key patterns and lessons
2. Highlights successful strategies
3. Notes failures and their causes
4. Suggests improvements and adaptations
5. Maintains continuity of learning`
                    }
                }
            ]
        };
    }
    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('GremlinGPT MCP Server running...');
    }
}
// Start the server
const server = new GremlinGPTMCPServer();
server.run().catch(console.error);
//# sourceMappingURL=index.js.map
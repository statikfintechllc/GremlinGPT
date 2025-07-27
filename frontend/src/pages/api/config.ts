import type { APIRoute } from 'astro';
import { readFile, writeFile } from 'fs/promises';
import { join } from 'path';

export const prerender = false;

// Get GremlinGPT root directory
const GREMLIN_ROOT = process.env.GREMLIN_ROOT || join(process.cwd(), '..');

export const GET: APIRoute = async ({ request }) => {
  const url = new URL(request.url);
  const configType = url.searchParams.get('type') || 'main';
  
  try {
    let configPath: string;
    let contentType: string;
    
    switch (configType) {
      case 'main':
        configPath = join(GREMLIN_ROOT, 'config', 'config.toml');
        contentType = 'text/plain';
        break;
      case 'memory':
        configPath = join(GREMLIN_ROOT, 'config', 'memory.json');
        contentType = 'application/json';
        break;
      case 'all':
        // Return all configuration files
        const mainConfig = await readFile(join(GREMLIN_ROOT, 'config', 'config.toml'), 'utf-8');
        const memoryConfig = await readFile(join(GREMLIN_ROOT, 'config', 'memory.json'), 'utf-8');
        
        return new Response(JSON.stringify({
          success: true,
          configs: {
            main: {
              path: 'config/config.toml',
              content: mainConfig,
              type: 'toml'
            },
            memory: {
              path: 'config/memory.json',
              content: memoryConfig,
              type: 'json'
            }
          }
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        });
      default:
        return new Response(JSON.stringify({ error: 'Invalid config type' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
    }

    const content = await readFile(configPath, 'utf-8');
    
    return new Response(JSON.stringify({
      success: true,
      content: content,
      path: configPath.replace(GREMLIN_ROOT, ''),
      type: configType
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Error reading config:', error);
    return new Response(JSON.stringify({ 
      error: 'Cannot read configuration file',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const PUT: APIRoute = async ({ request }) => {
  const url = new URL(request.url);
  const configType = url.searchParams.get('type') || 'main';
  
  try {
    let configPath: string;
    
    switch (configType) {
      case 'main':
        configPath = join(GREMLIN_ROOT, 'config', 'config.toml');
        break;
      case 'memory':
        configPath = join(GREMLIN_ROOT, 'config', 'memory.json');
        break;
      default:
        return new Response(JSON.stringify({ error: 'Invalid config type' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
    }

    const body = await request.json();
    const content = body.content;
    
    if (!content) {
      return new Response(JSON.stringify({ error: 'Content is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Validate JSON if it's a JSON config
    if (configType === 'memory') {
      try {
        JSON.parse(content);
      } catch (error) {
        return new Response(JSON.stringify({ 
          error: 'Invalid JSON format',
          details: error instanceof Error ? error.message : 'JSON parse error'
        }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }

    await writeFile(configPath, content, 'utf-8');
    
    return new Response(JSON.stringify({ 
      success: true, 
      message: `Configuration ${configType} saved successfully`,
      path: configPath.replace(GREMLIN_ROOT, '')
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Error saving config:', error);
    return new Response(JSON.stringify({ 
      error: 'Cannot save configuration file',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
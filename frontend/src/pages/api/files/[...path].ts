import type { APIRoute } from 'astro';
import { readFile, writeFile } from 'fs/promises';
import { join } from 'path';

export const prerender = false;

// Get GremlinGPT root directory
const GREMLIN_ROOT = process.env.GREMLIN_ROOT || join(process.cwd(), '..');

export const GET: APIRoute = async ({ params, request }) => {
  const url = new URL(request.url);
  const filePath = url.pathname.replace('/api/files', '');
  
  if (!filePath || filePath === '/') {
    return new Response(JSON.stringify({ error: 'File path required' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const fullPath = join(GREMLIN_ROOT, filePath);
    
    // Security check: ensure path is within GremlinGPT directory
    if (!fullPath.startsWith(GREMLIN_ROOT)) {
      return new Response(JSON.stringify({ error: 'Access denied' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const content = await readFile(fullPath, 'utf-8');
    
    return new Response(content, {
      status: 200,
      headers: { 'Content-Type': 'text/plain' }
    });
    
  } catch (error) {
    console.error('Error reading file:', error);
    return new Response(JSON.stringify({ error: 'File not found or cannot be read' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const PUT: APIRoute = async ({ params, request }) => {
  const url = new URL(request.url);
  const filePath = url.pathname.replace('/api/files', '');
  
  if (!filePath || filePath === '/') {
    return new Response(JSON.stringify({ error: 'File path required' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const fullPath = join(GREMLIN_ROOT, filePath);
    
    // Security check: ensure path is within GremlinGPT directory
    if (!fullPath.startsWith(GREMLIN_ROOT)) {
      return new Response(JSON.stringify({ error: 'Access denied' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const content = await request.text();
    await writeFile(fullPath, content, 'utf-8');
    
    return new Response(JSON.stringify({ success: true, message: 'File saved successfully' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Error writing file:', error);
    return new Response(JSON.stringify({ error: 'Cannot save file' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
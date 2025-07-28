import type { APIRoute } from 'astro';
import { readdir, stat } from 'fs/promises';
import { join } from 'path';

export const prerender = false;

// Get GremlinGPT root directory
const GREMLIN_ROOT = process.env.GREMLIN_ROOT || join(process.cwd(), '..');

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  children?: FileNode[];
}

// Files and directories to ignore
const IGNORE_PATTERNS = [
  '.git',
  '__pycache__',
  'node_modules',
  '.DS_Store',
  'dist',
  'build',
  '.env',
  'nohup.out',
  '.pytest_cache',
  '.coverage',
  '*.pyc',
  '*.log',
  'dist-electron'
];

function shouldIgnore(name: string): boolean {
  return IGNORE_PATTERNS.some(pattern => {
    if (pattern.includes('*')) {
      const regex = new RegExp(pattern.replace('*', '.*'));
      return regex.test(name);
    }
    return name === pattern;
  });
}

async function buildFileTree(dirPath: string, relativePath: string = ''): Promise<FileNode[]> {
  try {
    const entries = await readdir(dirPath);
    const nodes: FileNode[] = [];

    for (const entry of entries) {
      if (shouldIgnore(entry)) continue;

      const fullPath = join(dirPath, entry);
      const entryRelativePath = relativePath ? `${relativePath}/${entry}` : `/${entry}`;
      
      try {
        const stats = await stat(fullPath);
        
        if (stats.isDirectory()) {
          const children = await buildFileTree(fullPath, entryRelativePath);
          nodes.push({
            name: entry,
            path: entryRelativePath,
            type: 'directory',
            children: children.sort((a, b) => {
              // Sort directories first, then files, both alphabetically
              if (a.type !== b.type) {
                return a.type === 'directory' ? -1 : 1;
              }
              return a.name.localeCompare(b.name);
            })
          });
        } else {
          nodes.push({
            name: entry,
            path: entryRelativePath,
            type: 'file',
            size: stats.size
          });
        }
      } catch (error) {
        // Skip files/directories that can't be accessed
        continue;
      }
    }

    return nodes.sort((a, b) => {
      // Sort directories first, then files, both alphabetically
      if (a.type !== b.type) {
        return a.type === 'directory' ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });
  } catch (error) {
    console.error('Error building file tree:', error);
    return [];
  }
}

export const GET: APIRoute = async ({ request }) => {
  const url = new URL(request.url);
  const path = url.searchParams.get('path') || '';
  
  try {
    const targetPath = path ? join(GREMLIN_ROOT, path) : GREMLIN_ROOT;
    
    // Security check: ensure path is within GremlinGPT directory
    if (!targetPath.startsWith(GREMLIN_ROOT)) {
      return new Response(JSON.stringify({ error: 'Access denied' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const fileTree = await buildFileTree(targetPath, path);
    
    return new Response(JSON.stringify({ 
      success: true, 
      tree: fileTree,
      root: GREMLIN_ROOT
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Error fetching file tree:', error);
    return new Response(JSON.stringify({ 
      error: 'Cannot fetch file tree',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
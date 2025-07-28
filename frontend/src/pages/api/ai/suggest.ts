import type { APIRoute } from 'astro';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  try {
    const { code, file, selection } = await request.json();
    
    // For now, we'll create a mock AI suggestion
    // In a real implementation, this would integrate with the GremlinGPT AI system
    const suggestion = {
      type: 'code_suggestion',
      original: code,
      suggested: generateMockSuggestion(code, file),
      explanation: 'AI-generated code improvement suggestion',
      confidence: 0.85,
      file: file,
      selection: selection,
      timestamp: new Date().toISOString()
    };

    return new Response(JSON.stringify(suggestion), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('AI suggestion error:', error);
    return new Response(JSON.stringify({ error: 'AI suggestion failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

function generateMockSuggestion(code: string, file: string): string {
  // Mock AI suggestions based on file type and content
  const fileExt = file?.split('.').pop()?.toLowerCase();
  
  if (fileExt === 'py') {
    // Python-specific suggestions
    if (code.includes('import')) {
      return code + '\n# AI Suggestion: Consider using more specific imports for better performance';
    }
    if (code.includes('def ')) {
      return code + '\n# AI Suggestion: Add type hints for better code documentation';
    }
    if (code.includes('print(')) {
      return code.replace(/print\(/g, 'logger.info(') + '\n# AI Suggestion: Use logging instead of print statements';
    }
  }
  
  if (fileExt === 'js' || fileExt === 'ts') {
    // JavaScript/TypeScript suggestions
    if (code.includes('var ')) {
      return code.replace(/var /g, 'const ') + '\n// AI Suggestion: Use const/let instead of var';
    }
    if (code.includes('function ')) {
      return code + '\n// AI Suggestion: Consider using arrow functions for cleaner syntax';
    }
  }
  
  if (fileExt === 'sh') {
    // Shell script suggestions
    if (!code.includes('#!/bin/bash')) {
      return '#!/bin/bash\n' + code + '\n# AI Suggestion: Always include shebang for shell scripts';
    }
  }
  
  // Generic suggestions
  if (code.includes('TODO')) {
    return code + '\n# AI Suggestion: Consider creating a GitHub issue for this TODO item';
  }
  
  if (code.includes('FIXME')) {
    return code + '\n# AI Suggestion: High priority fix needed - consider addressing immediately';
  }
  
  return code + '\n# AI Suggestion: Code looks good - consider adding comments for clarity';
}
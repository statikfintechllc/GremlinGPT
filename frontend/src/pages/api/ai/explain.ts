import type { APIRoute } from 'astro';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  try {
    const { code, file } = await request.json();
    
    // Generate mock AI explanation
    const explanation = generateMockExplanation(code, file);

    return new Response(JSON.stringify(explanation), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('AI explanation error:', error);
    return new Response(JSON.stringify({ error: 'AI explanation failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

function generateMockExplanation(code: string, file: string) {
  const fileExt = file?.split('.').pop()?.toLowerCase();
  const lines = code.split('\n').length;
  const hasImports = code.includes('import') || code.includes('from ') || code.includes('require(');
  const hasFunctions = code.includes('def ') || code.includes('function ') || code.includes('=>');
  const hasClasses = code.includes('class ');
  
  let explanation = {
    type: 'code_explanation',
    file: file,
    summary: '',
    details: [],
    complexity: 'low',
    suggestions: [],
    timestamp: new Date().toISOString()
  };

  // Generate summary based on file type and content
  if (fileExt === 'py') {
    explanation.summary = `Python ${hasClasses ? 'class' : hasFunctions ? 'module' : 'script'} with ${lines} lines of code.`;
    
    if (hasImports) {
      explanation.details.push('This file imports external dependencies for extended functionality.');
    }
    
    if (hasClasses) {
      explanation.details.push('Defines class(es) following object-oriented programming principles.');
      explanation.complexity = 'medium';
    }
    
    if (hasFunctions) {
      explanation.details.push('Contains function definitions for modular code organization.');
    }
    
    if (code.includes('async ') || code.includes('await ')) {
      explanation.details.push('Uses asynchronous programming patterns for non-blocking operations.');
      explanation.complexity = 'high';
    }
    
    explanation.suggestions.push('Consider adding docstrings for better code documentation.');
    explanation.suggestions.push('Use type hints to improve code readability and IDE support.');
    
  } else if (fileExt === 'js' || fileExt === 'ts') {
    explanation.summary = `${fileExt === 'ts' ? 'TypeScript' : 'JavaScript'} ${hasFunctions ? 'module' : 'script'} with ${lines} lines of code.`;
    
    if (hasImports) {
      explanation.details.push('Uses ES6+ import/export syntax for module management.');
    }
    
    if (code.includes('class ')) {
      explanation.details.push('Implements ES6 class syntax for object-oriented programming.');
      explanation.complexity = 'medium';
    }
    
    if (code.includes('async ') || code.includes('await ') || code.includes('Promise')) {
      explanation.details.push('Handles asynchronous operations using modern JavaScript patterns.');
      explanation.complexity = 'high';
    }
    
    if (fileExt === 'ts') {
      explanation.suggestions.push('Leverage TypeScript\'s type system for better code safety.');
    }
    
    explanation.suggestions.push('Consider using JSDoc comments for function documentation.');
    
  } else if (fileExt === 'sh') {
    explanation.summary = `Shell script with ${lines} lines for system automation.`;
    explanation.details.push('Bash script for command-line operations and system administration.');
    
    if (code.includes('function ') || code.includes('() {')) {
      explanation.details.push('Defines shell functions for code reusability.');
    }
    
    if (code.includes('if ') || code.includes('case ')) {
      explanation.details.push('Uses conditional logic for decision-making.');
    }
    
    explanation.suggestions.push('Add error checking with set -e for safer script execution.');
    explanation.suggestions.push('Use shellcheck for script validation and best practices.');
    
  } else if (fileExt === 'json') {
    explanation.summary = `JSON configuration file with structured data.`;
    explanation.details.push('Contains structured data in JSON format for configuration or data exchange.');
    explanation.suggestions.push('Validate JSON syntax to ensure proper formatting.');
    
  } else if (fileExt === 'md') {
    explanation.summary = `Markdown documentation with ${lines} lines.`;
    explanation.details.push('Markdown file for documentation, README, or content creation.');
    explanation.suggestions.push('Follow Markdown best practices for better readability.');
    
  } else {
    explanation.summary = `Source file with ${lines} lines of code.`;
    explanation.details.push('General source code file - consider specific analysis based on language.');
  }

  // Set complexity based on lines and content
  if (lines > 100) {
    explanation.complexity = 'high';
  } else if (lines > 50) {
    explanation.complexity = 'medium';
  }

  return explanation;
}
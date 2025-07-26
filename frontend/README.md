# GremlinGPT Frontend - Astro + Tailwind + Monaco + Electron

## Overview

This is the completely migrated GremlinGPT frontend, replacing the previous VS Code extension with a standalone Electron application featuring:

- **Astro**: Modern web framework for fast, content-focused websites
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Monaco Editor**: The same code editor that powers VS Code, embedded directly
- **Electron**: Cross-platform desktop application framework

## Architecture

```
GremlinGPT Frontend/
├── src/
│   ├── layouts/
│   │   └── Layout.astro          # Main layout component
│   ├── pages/
│   │   ├── index.astro           # Main application page
│   │   └── api/                  # API routes
│   │       ├── files/[...path].ts    # File operations API
│   │       └── ai/               # AI integration APIs
│   │           ├── suggest.ts    # AI code suggestions
│   │           └── explain.ts    # AI code explanations
│   ├── components/
│   │   ├── FileTree.astro        # File tree navigation
│   │   ├── MonacoEditor.astro    # Monaco editor integration
│   │   └── Tabs.astro            # File tab management
│   └── styles/
│       └── global.css            # Global styles with Tailwind
├── main.cjs                      # Electron main process
├── preload.cjs                   # Electron preload script
└── dist/                         # Build output
    ├── client/                   # Client-side assets
    └── server/                   # Server-side code
```

## Key Features

### 🎯 Source Code Editor
- **Monaco Editor**: Full-featured code editor with syntax highlighting
- **File Tree Navigation**: Browse and open GremlinGPT source files
- **Multi-tab Interface**: Work with multiple files simultaneously
- **Auto-save**: Automatically saves changes after 2 seconds of inactivity

### 🤖 AI Integration
- **AI Suggestions**: Get AI-powered code improvement suggestions (Ctrl+I)
- **AI Explanations**: Get detailed explanations of code sections (Ctrl+E)
- **Real-time Integration**: AI agent can suggest changes directly in the editor
- **Contextual Analysis**: AI understands the file type and provides relevant suggestions

### 🖥️ Desktop Application
- **Electron Wrapper**: Native desktop application experience
- **File System Access**: Direct access to GremlinGPT source files
- **Offline Capability**: Fully functional without internet connection
- **Cross-platform**: Runs on Windows, macOS, and Linux

### 🎨 Modern UI
- **Dark Theme**: Gremlin-themed dark interface
- **Responsive Design**: Adapts to different screen sizes
- **Tailwind CSS**: Utility-first styling for consistent design
- **Real-time Updates**: File changes reflected immediately

## Development

### Prerequisites
- Node.js 18 or later
- npm 9 or later

### Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Start Electron in development mode (separate terminal)
npm run electron-dev
```

### Available Scripts
- `npm run dev` - Start Astro development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run electron` - Start Electron app
- `npm run electron-dev` - Start Electron with dev server
- `npm run dist` - Build and package Electron app

## Production Build

### Build Application
```bash
# Build Astro application
npm run build

# Package as Electron app
npm run dist
```

### File Structure After Build
```
dist/
├── client/           # Static client assets
├── server/           # Server-side code
└── dist-electron/    # Packaged Electron app
```

## API Endpoints

### File Operations
- `GET /api/files/[path]` - Read file content
- `PUT /api/files/[path]` - Write file content

### AI Integration
- `POST /api/ai/suggest` - Get AI suggestions for code
- `POST /api/ai/explain` - Get AI explanations for code

## Keyboard Shortcuts

### Editor
- `Ctrl+S` - Save current file
- `Ctrl+N` - New file
- `Ctrl+W` - Close current tab
- `Ctrl+T` - New tab
- `Ctrl+F` - Find in file
- `Ctrl+H` - Find and replace

### AI Features
- `Ctrl+I` - AI suggest changes
- `Ctrl+E` - AI explain code

## Configuration

### Environment Variables
- `GREMLIN_ROOT` - Path to GremlinGPT root directory (auto-detected)
- `NODE_ENV` - Environment mode (development/production)

### Electron Configuration
The Electron app is configured to:
- Watch GremlinGPT source files for changes
- Provide secure file system access
- Enable AI agent communication via WebSocket
- Support offline operation

## Integration with GremlinGPT

This frontend integrates with the GremlinGPT ecosystem by:

1. **File System Access**: Direct read/write access to all GremlinGPT source files
2. **AI Agent Communication**: WebSocket connection for real-time AI suggestions
3. **Backend Integration**: API routes that can connect to GremlinGPT's backend systems
4. **Live Updates**: File watcher that reflects changes made by other GremlinGPT processes

## Security

- **Sandboxed Renderer**: Electron renderer process runs in a secure sandbox
- **Preload Script**: Secure bridge between main and renderer processes
- **Path Validation**: All file operations are validated to prevent directory traversal
- **No External Dependencies**: Fully offline, no cloud connections required

## Migration from VS Code Extension

This replaces the previous VS Code extension with several advantages:

1. **Standalone Application**: No dependency on VS Code installation
2. **Better Integration**: Direct file system access without VS Code limitations
3. **Enhanced UI**: Custom interface designed specifically for GremlinGPT
4. **AI Focus**: Built-in AI features rather than extension-based
5. **Offline First**: No external dependencies or cloud services

## Troubleshooting

### Common Issues

1. **Build Errors**: Ensure Node.js 18+ and run `npm install`
2. **Electron Startup**: In headless environments, use `--no-sandbox` flag
3. **File Access**: Ensure proper permissions on GremlinGPT directory
4. **Monaco Loading**: Check network connectivity for CDN resources

### Debug Mode
```bash
# Enable debug logging
NODE_ENV=development npm run electron
```

### Testing
```bash
# Run build validation
./test-build.sh
```

## Contributing

When contributing to the frontend:

1. Follow the existing Astro + Tailwind patterns
2. Test changes in both development and production builds
3. Ensure Electron integration remains functional
4. Validate AI API endpoints work correctly
5. Test file operations with actual GremlinGPT files

## License

This frontend is part of the GremlinGPT project and follows the same licensing terms.

---

Built with ❤️ by StatikFintechLLC for the GremlinGPT Autonomous AI System.
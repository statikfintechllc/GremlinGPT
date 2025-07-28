const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, content) => ipcRenderer.invoke('write-file', filePath, content),
  listDirectory: (dirPath) => ipcRenderer.invoke('list-directory', dirPath),
  getGremlinRoot: () => ipcRenderer.invoke('get-gremlin-root'),

  // Menu actions
  onMenuAction: (callback) => ipcRenderer.on('menu-action', callback),
  removeMenuActionListeners: () => ipcRenderer.removeAllListeners('menu-action'),

  // File watching
  onFileChanged: (callback) => ipcRenderer.on('file-changed', callback),
  onFileAdded: (callback) => ipcRenderer.on('file-added', callback),
  onFileDeleted: (callback) => ipcRenderer.on('file-deleted', callback),
  removeFileWatchListeners: () => {
    ipcRenderer.removeAllListeners('file-changed');
    ipcRenderer.removeAllListeners('file-added');
    ipcRenderer.removeAllListeners('file-deleted');
  },

  // AI integration
  onAISuggestion: (callback) => ipcRenderer.on('ai-suggestion', callback),
  onFileEditRequest: (callback) => ipcRenderer.on('file-edit-request', callback),
  onSystemStatus: (callback) => ipcRenderer.on('system-status', callback),
  removeAIListeners: () => {
    ipcRenderer.removeAllListeners('ai-suggestion');
    ipcRenderer.removeAllListeners('file-edit-request');
    ipcRenderer.removeAllListeners('system-status');
  },

  // Platform info
  platform: process.platform,
  
  // App version
  version: require('./package.json').version || '1.0.3'
});

// Global GremlinGPT API for the renderer
contextBridge.exposeInMainWorld('GremlinGPT', {
  // System information
  getSystemInfo: () => ({
    platform: process.platform,
    arch: process.arch,
    version: process.versions.electron,
    node: process.versions.node,
    chrome: process.versions.chrome
  }),

  // File system operations with GremlinGPT context
  fileSystem: {
    read: (filePath) => ipcRenderer.invoke('read-file', filePath),
    write: (filePath, content) => ipcRenderer.invoke('write-file', filePath, content),
    list: (dirPath) => ipcRenderer.invoke('list-directory', dirPath),
    getRootPath: () => ipcRenderer.invoke('get-gremlin-root')
  },

  // Events
  events: {
    on: (event, callback) => {
      const validEvents = [
        'menu-action', 'file-changed', 'file-added', 'file-deleted',
        'ai-suggestion', 'file-edit-request', 'system-status'
      ];
      if (validEvents.includes(event)) {
        ipcRenderer.on(event, callback);
      }
    },
    off: (event, callback) => {
      ipcRenderer.removeListener(event, callback);
    },
    removeAll: (event) => {
      ipcRenderer.removeAllListeners(event);
    }
  },

  // Utilities
  utils: {
    isElectron: true,
    isDevelopment: process.env.NODE_ENV === 'development',
    getPath: (name) => {
      // Common paths that might be useful
      const paths = {
        home: require('os').homedir(),
        temp: require('os').tmpdir()
      };
      return paths[name] || null;
    }
  }
});

// Console logging for debugging in development
if (process.env.NODE_ENV === 'development') {
  contextBridge.exposeInMainWorld('debug', {
    log: (...args) => console.log('[Preload]', ...args),
    error: (...args) => console.error('[Preload]', ...args),
    warn: (...args) => console.warn('[Preload]', ...args)
  });
}
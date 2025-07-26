const { app, BrowserWindow, Menu, dialog, ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs').promises;
const chokidar = require('chokidar');
const WebSocket = require('ws');
const { spawn } = require('child_process');

// Keep a global reference of the window object
let mainWindow;
let fileWatcher;
let wsServer;
let astroProcess;

// GremlinGPT root directory (parent of frontend)
const GREMLIN_ROOT = path.join(__dirname, '..');

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, 'public', 'favicon.svg'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.cjs')
    },
    show: false,
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    titleBarOverlay: process.platform !== 'darwin' ? {
      color: '#1f2937',
      symbolColor: '#c9d1d9'
    } : undefined
  });

  // Start Astro server and load the app
  startAstroServer().then(() => {
    mainWindow.loadURL('http://localhost:4321');
    
    if (process.env.NODE_ENV === 'development') {
      mainWindow.webContents.openDevTools();
    }
  });

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Focus on window
    if (process.platform === 'darwin') {
      app.dock.show();
    }
    mainWindow.focus();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
    stopFileWatcher();
    stopWebSocketServer();
    stopAstroServer();
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  return mainWindow;
}

async function startAstroServer() {
  return new Promise((resolve, reject) => {
    // Check if we're in development or production
    const isDev = process.env.NODE_ENV === 'development';
    
    if (isDev) {
      // In development, we expect the dev server to already be running
      resolve();
      return;
    }
    
    // In production, start the Astro server
    const serverPath = path.join(__dirname, 'dist', 'server', 'entry.mjs');
    
    astroProcess = spawn('node', [serverPath], {
      cwd: __dirname,
      env: {
        ...process.env,
        HOST: '127.0.0.1',
        PORT: '4321',
        GREMLIN_ROOT: GREMLIN_ROOT
      },
      stdio: 'pipe'
    });
    
    astroProcess.stdout.on('data', (data) => {
      console.log('[Astro]', data.toString());
    });
    
    astroProcess.stderr.on('data', (data) => {
      console.error('[Astro Error]', data.toString());
    });
    
    astroProcess.on('error', (error) => {
      console.error('Failed to start Astro server:', error);
      reject(error);
    });
    
    // Wait a moment for the server to start
    setTimeout(() => {
      resolve();
    }, 2000);
  });
}

function stopAstroServer() {
  if (astroProcess) {
    astroProcess.kill();
    astroProcess = null;
  }
}

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New File',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('menu-action', 'new-file');
          }
        },
        {
          label: 'Open File',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog(mainWindow, {
              properties: ['openFile'],
              defaultPath: GREMLIN_ROOT,
              filters: [
                { name: 'Python Files', extensions: ['py'] },
                { name: 'JavaScript Files', extensions: ['js', 'ts'] },
                { name: 'JSON Files', extensions: ['json'] },
                { name: 'Markdown Files', extensions: ['md'] },
                { name: 'Shell Scripts', extensions: ['sh'] },
                { name: 'All Files', extensions: ['*'] }
              ]
            });
            
            if (!result.canceled && result.filePaths.length > 0) {
              const filePath = result.filePaths[0];
              const relativePath = path.relative(GREMLIN_ROOT, filePath);
              mainWindow.webContents.send('menu-action', 'open-file', '/' + relativePath);
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Save',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            mainWindow.webContents.send('menu-action', 'save-file');
          }
        },
        {
          label: 'Save All',
          accelerator: 'CmdOrCtrl+Alt+S',
          click: () => {
            mainWindow.webContents.send('menu-action', 'save-all');
          }
        },
        { type: 'separator' },
        {
          label: 'Close Tab',
          accelerator: 'CmdOrCtrl+W',
          click: () => {
            mainWindow.webContents.send('menu-action', 'close-tab');
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectall' },
        { type: 'separator' },
        {
          label: 'Find',
          accelerator: 'CmdOrCtrl+F',
          click: () => {
            mainWindow.webContents.send('menu-action', 'find');
          }
        },
        {
          label: 'Replace',
          accelerator: 'CmdOrCtrl+H',
          click: () => {
            mainWindow.webContents.send('menu-action', 'replace');
          }
        }
      ]
    },
    {
      label: 'AI',
      submenu: [
        {
          label: 'AI Suggest Changes',
          accelerator: 'CmdOrCtrl+I',
          click: () => {
            mainWindow.webContents.send('menu-action', 'ai-suggest');
          }
        },
        {
          label: 'AI Explain Code',
          accelerator: 'CmdOrCtrl+E',
          click: () => {
            mainWindow.webContents.send('menu-action', 'ai-explain');
          }
        },
        { type: 'separator' },
        {
          label: 'Start GremlinGPT System',
          click: () => {
            mainWindow.webContents.send('menu-action', 'start-system');
          }
        },
        {
          label: 'Stop GremlinGPT System',
          click: () => {
            mainWindow.webContents.send('menu-action', 'stop-system');
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
        { type: 'separator' },
        {
          label: 'Toggle File Tree',
          accelerator: 'CmdOrCtrl+B',
          click: () => {
            mainWindow.webContents.send('menu-action', 'toggle-file-tree');
          }
        }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    }
  ];

  if (process.platform === 'darwin') {
    template.unshift({
      label: app.getName(),
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    });

    // Window menu
    template[5].submenu = [
      { role: 'close' },
      { role: 'minimize' },
      { role: 'zoom' },
      { type: 'separator' },
      { role: 'front' }
    ];
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

function startFileWatcher() {
  // Watch the GremlinGPT source files for changes
  fileWatcher = chokidar.watch(GREMLIN_ROOT, {
    ignored: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/.git/**',
      '**/frontend/**',
      '**/__pycache__/**',
      '**/*.pyc'
    ],
    persistent: true,
    ignoreInitial: true
  });

  fileWatcher
    .on('change', (filePath) => {
      const relativePath = '/' + path.relative(GREMLIN_ROOT, filePath);
      if (mainWindow) {
        mainWindow.webContents.send('file-changed', relativePath);
      }
    })
    .on('add', (filePath) => {
      const relativePath = '/' + path.relative(GREMLIN_ROOT, filePath);
      if (mainWindow) {
        mainWindow.webContents.send('file-added', relativePath);
      }
    })
    .on('unlink', (filePath) => {
      const relativePath = '/' + path.relative(GREMLIN_ROOT, filePath);
      if (mainWindow) {
        mainWindow.webContents.send('file-deleted', relativePath);
      }
    });
}

function stopFileWatcher() {
  if (fileWatcher) {
    fileWatcher.close();
    fileWatcher = null;
  }
}

function startWebSocketServer() {
  wsServer = new WebSocket.Server({ port: 8765 });
  
  wsServer.on('connection', (ws) => {
    console.log('WebSocket client connected');
    
    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message);
        handleWebSocketMessage(data, ws);
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    });
    
    ws.on('close', () => {
      console.log('WebSocket client disconnected');
    });
  });
}

function stopWebSocketServer() {
  if (wsServer) {
    wsServer.close();
    wsServer = null;
  }
}

function handleWebSocketMessage(data, ws) {
  // Handle messages from GremlinGPT AI agent
  switch (data.type) {
    case 'ai_suggestion':
      if (mainWindow) {
        mainWindow.webContents.send('ai-suggestion', data);
      }
      break;
    case 'file_edit_request':
      if (mainWindow) {
        mainWindow.webContents.send('file-edit-request', data);
      }
      break;
    case 'system_status':
      if (mainWindow) {
        mainWindow.webContents.send('system-status', data);
      }
      break;
  }
}

// IPC Handlers
ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const fullPath = path.join(GREMLIN_ROOT, filePath);
    const content = await fs.readFile(fullPath, 'utf8');
    return { success: true, content };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('write-file', async (event, filePath, content) => {
  try {
    const fullPath = path.join(GREMLIN_ROOT, filePath);
    await fs.writeFile(fullPath, content, 'utf8');
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('list-directory', async (event, dirPath) => {
  try {
    const fullPath = path.join(GREMLIN_ROOT, dirPath);
    const items = await fs.readdir(fullPath, { withFileTypes: true });
    
    const result = items.map(item => ({
      name: item.name,
      isDirectory: item.isDirectory(),
      path: path.join(dirPath, item.name).replace(/\\/g, '/')
    }));
    
    return { success: true, items: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-gremlin-root', () => {
  return GREMLIN_ROOT;
});

// App event handlers
app.whenReady().then(() => {
  createWindow();
  createMenu();
  startFileWatcher();
  startWebSocketServer();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopFileWatcher();
  stopWebSocketServer();
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});
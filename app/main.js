// app/main.js
const { app, BrowserWindow, Menu, ipcMain } = require('electron'); // Added ipcMain
const path = require('path');
// const { spawn } = require('child_process'); // For potentially starting Flask backend

// let flaskProcess = null; // Example: Flask process management

function createMainWindow () {
  const mainWindow = new BrowserWindow({
    width: 1280, // Slightly wider for better UI
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), // Correct path within app/
      contextIsolation: true,
      nodeIntegration: false, // Keep false for security
      devTools: true // Enable DevTools by default for development
    },
    icon: path.join(__dirname, 'assets', 'icon.png') // Example icon path
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html')); // Correct path within app/

  // Optional: Remove default Electron menu or set custom menu
  // Menu.setApplicationMenu(null); // Removes menu
  // Or set a custom one:
  // const menuTemplate = [ /* ... your menu template ... */ ];
  // const customMenu = Menu.buildFromTemplate(menuTemplate);
  // Menu.setApplicationMenu(customMenu);

  // Automatically open DevTools if not in production (more robust check)
  if (!app.isPackaged) { // app.isPackaged is true when the app is packaged
      mainWindow.webContents.openDevTools();
  }
}

// Example: Function to start Flask backend (conceptual, needs robust implementation if used)
/*
function startFlaskBackend() {
  // Path to virtual environment python and backend script
  // This needs to be robust and configurable, especially for packaged apps
  const venvPython = process.platform === 'win32' 
    ? path.join(__dirname, '../../backend/venv/Scripts/python.exe') 
    : path.join(__dirname, '../../backend/venv/bin/python');
  const backendScript = path.join(__dirname, '../../backend/app.py');
  const backendDir = path.join(__dirname, '../../backend');

  console.log(`Attempting to start Flask backend using: ${venvPython}`);
  console.log(`Backend script: ${backendScript}`);
  console.log(`Backend CWD: ${backendDir}`);

  // Check if venvPython exists
  // const fs = require('fs');
  // if (!fs.existsSync(venvPython)) {
  //   console.error("Python interpreter in venv not found at:", venvPython);
  //   dialog.showErrorBox("Backend Error", "Python interpreter in venv not found. Please ensure the backend virtual environment is set up.");
  //   return;
  // }

  flaskProcess = spawn(venvPython, [backendScript], { cwd: backendDir });

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask stdout: ${data}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask stderr: ${data}`);
    // Consider showing an error to the user if Flask logs critical errors
  });

  flaskProcess.on('close', (code) => {
    console.log(`Flask process exited with code ${code}`);
    if (code !== 0) {
        // dialog.showErrorBox("Backend Error", `The backend process exited unexpectedly with code ${code}.`);
    }
    flaskProcess = null;
  });

  flaskProcess.on('error', (err) => {
    console.error('Failed to start Flask process:', err);
    // dialog.showErrorBox("Backend Startup Error", `Failed to start the backend process: ${err.message}.`);
    flaskProcess = null;
  });
}
*/

app.whenReady().then(() => {
  // if (!app.isPackaged) { // Example: Only start backend directly in dev mode
  //    startFlaskBackend();
  // }
  createMainWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    /*
    if (flaskProcess) {
      console.log('Attempting to kill Flask process...');
      const killed = flaskProcess.kill(); // SIGTERM by default
      if(!killed) {
        console.error('Failed to kill Flask process. It might need to be killed manually.');
      } else {
        console.log('Flask process killed.');
      }
    }
    */
    app.quit();
  }
});

// IPC Handlers
// Handler for the 'get-app-path' invoke call from preload.js
ipcMain.handle('get-app-path', () => {
  return app.getAppPath();
});

// Example: Basic IPC message listener
ipcMain.on('some-action', (event, arg) => {
  console.log('IPC message received on main process "some-action":', arg);
  // Do something and optionally reply
  event.reply('action-reply', 'Data from main process, action completed.');
});

app.on('before-quit', () => {
  // Explicitly kill flask process before quitting if it's running
  /*
  if (flaskProcess) {
    console.log('Killing Flask process before quit...');
    flaskProcess.kill();
  }
  */
});

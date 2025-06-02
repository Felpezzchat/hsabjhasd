// This skeleton would typically be located at:
// project_root/app/main.js OR project_root/main_electron.js
// For this skeleton, we assume it's in 'skeletons/' and needs to adjust paths accordingly.

const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process'); // To start/stop Flask backend

// --- Backend Process Management ---
let flaskProcess = null;
const flaskPort = 5001; // Ensure this matches the port in backend_app_skeleton.py

// Adjust paths for running from 'skeletons' directory
// In a real app, __dirname for 'app/main.js' would be 'project_root/app/'
const projectRoot = path.join(__dirname, '..'); // Goes up one level from 'skeletons' to project root
const backendAppPath = path.join(projectRoot, 'backend', 'backend_app_skeleton.py'); // Path to the backend script
const preloadScriptPath = path.join(projectRoot, 'app', 'preload.js'); // Path to preload script
const indexPath = path.join(projectRoot, 'app', 'index.html'); // Path to main HTML file

function startFlaskBackend() {
  console.log(`Starting Flask backend from: ${backendAppPath}`);
  // Ensure 'python' is in the system PATH. Or use an absolute path to python interpreter.
  // For packaged apps, you might need to bundle Python or use a different approach.
  flaskProcess = spawn('python', [backendAppPath]);

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask stdout: ${data.toString()}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask stderr: ${data.toString()}`);
    // Optionally, show an error dialog to the user if Flask fails to start
    // dialog.showErrorBox('Backend Error', `Flask process stderr: ${data.toString()}`);
  });

  flaskProcess.on('exit', (code) => {
    console.log(`Flask process exited with code ${code}`);
    flaskProcess = null;
    // Optionally, attempt to restart or notify the user
    // if (code !== 0) {
    //   dialog.showErrorBox('Backend Stopped', `The backend process stopped unexpectedly (code: ${code}). Please try restarting the application.`);
    // }
  });

  flaskProcess.on('error', (err) => {
    console.error('Failed to start Flask process:', err);
    dialog.showErrorBox('Backend Startup Error', `Failed to start the backend process: ${err.message}. Ensure Python is installed and accessible.`);
    flaskProcess = null;
  });
}

function stopFlaskBackend() {
  if (flaskProcess) {
    console.log('Stopping Flask backend...');
    flaskProcess.kill('SIGINT'); // Send SIGINT (Ctrl+C) to allow Flask to shut down gracefully
    // Consider a timeout and then flaskProcess.kill('SIGKILL') if it doesn't stop
  }
}

// --- Electron Window Creation ---
function createWindow () {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: preloadScriptPath, // Use the adjusted path
      contextIsolation: true,    // Recommended for security
      nodeIntegration: false,    // Recommended for security
      devTools: true             // Enable DevTools by default for skeleton
    }
  });

  console.log(`Loading index.html from: ${indexPath}`);
  mainWindow.loadFile(indexPath)
    .then(() => console.log("Index.html loaded successfully."))
    .catch(err => {
        console.error("Failed to load index.html:", err);
        dialog.showErrorBox("Load Error", `Failed to load the application UI: ${err.message}. Check if the file exists at ${indexPath}.`);
    });

  // Open the DevTools (optional)
  // mainWindow.webContents.openDevTools();
}

// --- Electron App Lifecycle ---
app.whenReady().then(() => {
  startFlaskBackend(); // Start Flask when Electron is ready
  createWindow();

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  // Quit when all windows are closed, except on macOS. There, it's common
  // for applications and their menu bar to stay active until the user quits
  // explicitly with Cmd + Q.
  if (process.platform !== 'darwin') {
    app.quit(); // This will trigger the 'will-quit' event
  }
});

app.on('will-quit', () => {
  // This event is emitted when Electron is about to quit.
  // We use this to ensure the Flask backend is stopped.
  stopFlaskBackend();
});


// --- IPC Handlers (Conceptual) ---
// Example: Handle a request from renderer process via preload script
ipcMain.handle('dialog:openFile', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog();
  if (canceled) {
    return null;
  } else {
    return filePaths[0];
  }
});

ipcMain.on('to-main', (event, args) => {
  console.log('Message from renderer:', args);
  // Example: send a reply back to the renderer that sent the message
  event.reply('from-main', 'Message received in main process. Thanks!');
});


// --- Notes for this skeleton ---
// 1. Path Adjustments: The paths `backendAppPath`, `preloadScriptPath`, and `indexPath`
//    are adjusted assuming this `electron_main_skeleton.js` file is in a `skeletons/` directory,
//    and the actual project structure (`app/`, `backend/`) is one level up.
//    In a real Electron app, if this file is `app/main.js`, `__dirname` would be `project_root/app/`,
//    so paths would be like `path.join(__dirname, '../backend/run.py')`.
//
// 2. Starting Backend: The `startFlaskBackend` function uses `child_process.spawn`.
//    - Ensure Python is in the system's PATH or provide an absolute path to the Python executable.
//    - For a packaged application, you'll need to either bundle a Python interpreter
//      or instruct users to install Python separately. Tools like PyInstaller can bundle Flask apps,
//      and then Electron could run the resulting executable.
//
// 3. Preload Script: `preload: preloadScriptPath` assumes you will create a `preload.js`
//    in `project_root/app/preload.js`. This is crucial for secure IPC if `contextIsolation` is true.
//
// 4. Error Handling: Basic error handling for Flask process is included. More robust
//    handling (e.g., retrying Flask start, user notifications) would be needed for a real app.
//
// To run this skeleton (conceptual steps, assuming you have an index.html and preload.js):
// 1. Save this file as `electron_main_skeleton.js` in the `skeletons` directory.
// 2. Ensure `backend_app_skeleton.py` is also in `skeletons`.
// 3. Create `../app/index.html` and `../app/preload.js` (relative to this file).
// 4. Install Electron: `npm install electron` (in the project root or globally for testing).
// 5. Run from project root: `electron skeletons/electron_main_skeleton.js`
//    (Or, if `package.json` in root has ` "main": "skeletons/electron_main_skeleton.js" `, just `npm start` or `electron .`)

console.log("Electron main process script loaded.");
console.log(`Project root (calculated): ${projectRoot}`);
console.log(`Backend app path: ${backendAppPath}`);
console.log(`Preload script path: ${preloadScriptPath}`);
console.log(`Index HTML path: ${indexPath}`);

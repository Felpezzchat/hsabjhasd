// This skeleton would typically be located at:
// project_root/app/scripts/renderer.js

console.log("Renderer script loaded.");

document.addEventListener('DOMContentLoaded', () => {
  const messageDiv = document.getElementById('message');
  if (messageDiv) {
    messageDiv.textContent = 'Hello from Electron Renderer! DOM fully loaded.';
  } else {
    console.error("#message div not found in HTML.");
  }

  const clientList = document.getElementById('clientList');
  if (!clientList) {
    console.error("#clientList ul not found in HTML.");
  }

  const addClientForm = document.getElementById('addClientForm');
  if (!addClientForm) {
    console.error("#addClientForm form not found in HTML.");
  }


  fetchClients();
  setupAddClientForm();
  setupTestIPC(); // Example for testing IPC
});

async function fetchClients() {
  const clientList = document.getElementById('clientList');
  if (!clientList) return;

  try {
    // Assuming Flask backend is running on port 5001 (as configured in backend_app_skeleton.py and electron_main_skeleton.js)
    const response = await fetch('http://localhost:5001/api/clients');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
    }
    const clients = await response.json();

    clientList.innerHTML = ''; // Clear existing list (e.g., "Loading clients...")
    if (clients.length === 0) {
        const listItem = document.createElement('li');
        listItem.textContent = 'No clients found in the database.';
        clientList.appendChild(listItem);
    } else {
        clients.forEach(client => {
          const listItem = document.createElement('li');
          listItem.textContent = `ID: ${client.id}, Name: ${client.name}, Email: ${client.email || 'N/A'}, Phone: ${client.phone || 'N/A'}`;
          clientList.appendChild(listItem);
        });
    }
  } catch (error) {
    console.error('Failed to fetch clients:', error);
    clientList.innerHTML = `<li>Error fetching clients: ${error.message}. Is the backend running on port 5001?</li>`;
  }
}

function setupAddClientForm() {
    const form = document.getElementById('addClientForm');
    const nameInput = document.getElementById('clientName');
    const emailInput = document.getElementById('clientEmail');
    const phoneInput = document.getElementById('clientPhone'); // Added phone input
    const formMessage = document.getElementById('formMessage');


    if (form && nameInput && emailInput && phoneInput && formMessage) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            formMessage.textContent = ''; // Clear previous messages

            const name = nameInput.value;
            const email = emailInput.value;
            const phone = phoneInput.value;

            if (!name) {
                formMessage.textContent = 'Client name is required.';
                formMessage.style.color = 'red';
                return;
            }

            try {
                const response = await fetch('http://localhost:5001/api/clients', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name, email, phone }), // Added phone
                });

                const responseData = await response.json(); // Try to parse JSON regardless of ok status for error details

                if (!response.ok) {
                    throw new Error(responseData.error || `HTTP error! status: ${response.status}`);
                }

                console.log('Client added:', responseData);
                formMessage.textContent = `Client "${responseData.name}" added successfully with ID ${responseData.id}!`;
                formMessage.style.color = 'green';

                nameInput.value = ''; // Clear form
                emailInput.value = '';
                phoneInput.value = ''; // Clear phone
                fetchClients(); // Refresh the list
            } catch (error) {
                console.error('Failed to add client:', error);
                formMessage.textContent = `Error adding client: ${error.message}`;
                formMessage.style.color = 'red';
            }
        });
    } else {
        console.error("One or more elements for 'addClientForm' not found.");
    }
}


// --- IPC Communication Example (using preload script) ---
function setupTestIPC() {
  const openFileButton = document.getElementById('openFileButton');
  const filePathElement = document.getElementById('filePath');
  const ipcTestButton = document.getElementById('ipcTestButton');
  const ipcResponseElement = document.getElementById('ipcResponse');


  if (openFileButton && filePathElement) {
    openFileButton.addEventListener('click', async () => {
      if (window.electronAPI && window.electronAPI.openFileDialog) {
        filePathElement.textContent = 'Opening dialog...';
        const path = await window.electronAPI.openFileDialog();
        if (path) {
          filePathElement.textContent = `Selected file: ${path}`;
        } else {
          filePathElement.textContent = 'File selection cancelled or no file selected.';
        }
      } else {
        filePathElement.textContent = 'Error: electronAPI.openFileDialog not found. Is preload.js configured?';
        console.error('window.electronAPI.openFileDialog is not defined. Check preload.js and contextIsolation settings.');
      }
    });
  } else {
    console.warn("'openFileButton' or 'filePathElement' not found. IPC 'openFile' test UI won't work.");
  }

  if (ipcTestButton && ipcResponseElement) {
    ipcTestButton.addEventListener('click', () => {
        if (window.electronAPI && window.electronAPI.sendMessageToMain) {
            ipcResponseElement.textContent = 'Sending message to main...';
            window.electronAPI.sendMessageToMain('Hello from Renderer via Preload!');
        } else {
            ipcResponseElement.textContent = 'Error: electronAPI.sendMessageToMain not found.';
            console.error('window.electronAPI.sendMessageToMain is not defined.');
        }
    });

    // Listen for replies from main process (if preload script sets this up)
    if (window.electronAPI && window.electronAPI.onReplyFromMain) {
        window.electronAPI.onReplyFromMain((event, message) => {
            console.log('Message from main received in renderer:', message);
            ipcResponseElement.textContent = `Main says: "${message}"`;
        });
    } else {
        console.warn("window.electronAPI.onReplyFromMain not set up in preload.");
    }

  } else {
    console.warn("'ipcTestButton' or 'ipcResponseElement' not found. Basic IPC test UI won't work.");
  }
}

// --- Notes for this skeleton ---
// 1. DOMContentLoaded: Ensures the script runs after the HTML is fully parsed.
// 2. Backend URL: `http://localhost:5001` must match the port your Flask backend is running on.
// 3. Error Handling: Basic error handling for fetch calls is included.
// 4. IPC: The `setupTestIPC` function demonstrates how you might interact with Electron's main
//    process APIs if they are exposed via a `preload.js` script (e.g., `window.electronAPI`).
//    This is the recommended way for secure IPC when `contextIsolation` is true.
//
// To use this skeleton:
// - Save it as `renderer.js` inside `project_root/app/scripts/`.
// - Ensure your `project_root/app/index.html` includes `<script src="../scripts/renderer.js"></script>`
//   (or `scripts/renderer.js` if index.html is also in `app/`).
// - Make sure you have an HTML structure that matches the IDs used (e.g., `message`, `clientList`, `addClientForm`).
// - For IPC examples to work, you'd need a `project_root/app/preload.js` like:
//   ```javascript
//   // project_root/app/preload.js
//   const { contextBridge, ipcRenderer } = require('electron');
//
//   contextBridge.exposeInMainWorld('electronAPI', {
//     openFileDialog: () => ipcRenderer.invoke('dialog:openFile'),
//     sendMessageToMain: (message) => ipcRenderer.send('to-main', message),
//     onReplyFromMain: (callback) => ipcRenderer.on('from-main', callback)
//     // Note: For ipcRenderer.on, it's better to return a function that removes the listener
//     // to prevent memory leaks if the component using it is destroyed and recreated.
//     // onReplyFromMain: (callback) => {
//     //   const listener = (event, ...args) => callback(...args);
//     //   ipcRenderer.on('from-main', listener);
//     //   return () => ipcRenderer.removeListener('from-main', listener); // Cleanup function
//     // }
//   });
//   console.log("Preload script executed, electronAPI exposed.");
//   ```
//   And corresponding handlers in your main process file (e.g., `electron_main_skeleton.js`).
//   `ipcMain.handle('dialog:openFile', ...)` and `ipcMain.on('to-main', ...)`
console.log("End of renderer.js");

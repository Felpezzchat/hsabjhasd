// app/preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Example: Expose a function to send an IPC message (one-way)
  send: (channel, data) => {
    // Whitelist channels
    const validChannelsSend = ['to-main-process'];
    if (validChannelsSend.includes(channel)) {
      ipcRenderer.send(channel, data);
    }
  },
  // Example: Expose a function to receive an IPC message
  receive: (channel, func) => {
    const validChannelsReceive = ['from-main-process'];
    if (validChannelsReceive.includes(channel)) {
      // Deliberately strip event as it includes `sender`
      const listener = (event, ...args) => func(...args);
      ipcRenderer.on(channel, listener);
      // Return a cleanup function
      return () => ipcRenderer.removeListener(channel, listener);
    }
  },
  // Example: Expose a function for two-way IPC (invoke/handle)
  invoke: (channel, data) => {
    const validChannelsInvoke = ['get-app-path', 'dialog:openFile']; // Add more as needed
    if (validChannelsInvoke.includes(channel)) {
      return ipcRenderer.invoke(channel, data);
    }
    // Optionally, throw an error or return a rejected promise for invalid channels
    return Promise.reject(new Error(`Invalid invoke channel: ${channel}`));
  }
  
  // We will add more specific functions as we build UI components that need them
  // e.g., for file dialogs, webcam access, etc.
});

console.log("preload.js executed and 'electronAPI' exposed.");

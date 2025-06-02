## Salon Management System Interaction Diagram

This diagram illustrates the basic interaction flow between the Electron Frontend, the Flask Backend, and the SQLite Database, as well as interactions with local system resources.

```mermaid
graph LR
    A[Electron Frontend UI (Renderer Process)] -- HTTP Requests (localhost:5001) --> B(Flask Backend API);
    B -- CRUD Operations (SQL Queries) --> C(SQLite Database - salon_data.sqlite);
    C -- Data Results --> B;
    B -- JSON Responses --> A;
    D(Electron Main Process - main.js) -- Manages Window & System Access --> A;
    D -- Can directly access/manage --> E(Local System Resources - e.g., Filesystem for Backups, Webcam);
    A -- Image Data (e.g., from webcam/file upload) --> B;
    B -- Saves Image Path to DB & Image to Filesystem --> E;
```

**Explanation of Components:**

*   **Electron Frontend UI (Renderer Process):** This is the user interface that the salon staff interacts with. It's built with HTML, CSS, and JavaScript. It makes HTTP requests to the local Flask backend to fetch or send data.
*   **Flask Backend API:** A Python Flask application running locally. It receives requests from the Electron frontend, performs business logic, and interacts with the SQLite database. It returns data in JSON format.
*   **SQLite Database:** A file-based database (e.g., `salon_data.sqlite`) that stores all persistent application data (client info, appointments, inventory, etc.).
*   **Electron Main Process:** This Node.js process controls the application lifecycle, creates UI windows, and has access to Electron's native APIs and Node.js modules. It can interact with the local file system directly (for tasks like backups or saving images captured via webcam) and manage inter-process communication (IPC) with renderer processes.
*   **Local System Resources:** Represents the computer's filesystem, webcam, printers, etc., that the Electron application (primarily through the main process or specific Electron APIs exposed to the renderer) can interact with.

**Typical Flow (e.g., Fetching Clients):**

1.  User action in Electron UI triggers a JavaScript function.
2.  JavaScript in the Renderer Process makes a `fetch` request to `http://localhost:5001/api/clients`.
3.  Flask Backend API receives the request, queries the SQLite Database for client data.
4.  SQLite Database returns the data to Flask.
5.  Flask formats the data as a JSON response and sends it back to the Electron Renderer Process.
6.  Electron UI updates to display the client list.

**Typical Flow (e.g., Adding a Client Photo via Webcam):**

1.  User clicks "Capture Photo" in Electron UI.
2.  Electron Renderer Process uses `navigator.mediaDevices.getUserMedia` to access the webcam.
3.  User captures photo; image data (e.g., base64 string or Blob) is obtained in the Renderer.
4.  Image data is sent via HTTP POST request to a Flask endpoint (e.g., `/api/clients/<id>/photo`).
5.  Flask Backend receives the image data, saves it as a file to a designated folder (e.g., `data/client_photos/`) and stores the file path and any metadata in the `ClientPhotos` table in the SQLite Database.
6.  Flask returns a success response.
7.  Electron UI updates to show the new photo.

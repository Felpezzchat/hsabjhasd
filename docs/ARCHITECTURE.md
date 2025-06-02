# Salon Management System Architecture

This document outlines the overall architecture and technology stack for the salon management system.

**Chosen Technologies:**

*   **Backend:** Python with Flask.
    *   *Reasoning:* Flask is a lightweight and flexible micro-framework, well-suited for creating a local API that the Electron frontend can communicate with. It's easy to start with and can scale if needed. Python has a rich ecosystem of libraries that can be leveraged for various functionalities.
*   **Frontend:** Electron.js.
    *   *Reasoning:* Electron allows building cross-platform desktop applications using web technologies (HTML, CSS, JavaScript). This is ideal for a local application that needs access to system resources like the webcam and local file system for backups. It also allows for a rich, customizable user interface.
*   **Database:** SQLite.
    *   *Reasoning:* SQLite is a serverless, file-based database engine. It's perfect for a local application as it doesn't require a separate database server to be running. Data is stored in a single file, making backups and data portability straightforward. It's also lightweight and efficient for the scale of this application.
*   **Frontend Web Technologies (within Electron):** HTML, CSS, JavaScript.
    *   *Reasoning:* Standard web technologies for building the user interface within the Electron shell. A modern JavaScript framework like React or Vue.js could be adopted for more complex UIs, but for the conceptual design, plain HTML/CSS/JS is sufficient to illustrate the structure.

**Interaction Model:**

1.  **Electron Main Process:** The Electron main process (`main.js` or similar) will be responsible for creating the application windows (BrowserWindow instances) and managing the application lifecycle.
2.  **Electron Renderer Process:** Each application window will run its own renderer process, which is essentially a Chromium browser environment. This is where the HTML, CSS, and JavaScript for the UI will execute.
3.  **Flask Backend Server:** A local Flask server will run in the background. This server will handle business logic, data processing, and database interactions.
4.  **Communication:**
    *   The Electron renderer process (frontend) will make HTTP requests (e.g., using `fetch` API) to the local Flask backend server (e.g., `http://localhost:5000/api/clients`).
    *   The Flask backend will process these requests, interact with the SQLite database, and return responses (typically in JSON format) to the frontend.
    *   For functionalities requiring direct hardware access (like webcam integration for client photos), Electron's main process or renderer process can use Node.js APIs and Electron-specific APIs (e.g., `desktopCapturer` or direct access to media devices). Data captured (like images) can then be sent to the backend for storage or processing if needed.

**Offline Capability:**

*   The entire system (Electron frontend, Flask backend, SQLite database) is designed to run locally on the user's computer without requiring an internet connection for core functionalities.
*   Data is stored locally in the SQLite database.
*   Backups are made to local or external drives.

**Future API Integration:**

*   The Flask backend will be designed with RESTful API endpoints from the start.
*   When internet connectivity is available, and future integrations are implemented, the Electron application (or the Flask backend itself) can make outbound requests to external APIs (e.g., payment gateways, notification services).
*   A synchronization mechanism will be conceptualized for syncing local data with external services if the application evolves to have a cloud component.

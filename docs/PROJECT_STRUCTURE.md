# Proposed Project Directory Structure

This document outlines a proposed directory structure for the Salon Management System. The structure is designed to logically organize the Electron frontend, Python/Flask backend, shared data, tests, and documentation.

```
salon_management_system/
├── app/                                # Electron frontend application
│   ├── main.js                         # Electron main process
│   ├── preload.js                      # Script to preload in renderer, if needed for contextBridge
│   ├── index.html                      # Main HTML file for the UI
│   ├── styles/                         # CSS files
│   │   └── main.css
│   ├── scripts/                        # Frontend JavaScript files
│   │   └── renderer.js                 # Main renderer process logic
│   │   └── api_client.js               # Optional: JS module for backend API calls
│   ├── assets/                         # UI assets (icons, images specific to UI)
│   │   └── icon.png
│   │   └── logo.png
│   └── package.json                    # Frontend dependencies and scripts (for Electron)
│
├── backend/                            # Flask backend application
│   ├── run.py                          # Main Flask application entry point (or app.py)
│   ├── config.py                       # Configuration settings (database URI, secret keys, API keys)
│   ├── requirements.txt                # Python dependencies
│   ├── instance/                       # Instance-specific data (e.g., overridden config, SQLite if not in /data)
│   │   └── config_override.py          # Example of instance-specific config
│   ├── app_factory.py                  # Optional: Application factory for Flask (create_app function)
│   ├── models/                         # Database models (e.g., SQLAlchemy models or plain DB interaction classes)
│   │   ├── __init__.py
│   │   ├── base.py                     # Base model or common DB utilities
│   │   ├── customer.py
│   │   ├── appointment.py
│   │   ├── product.py
│   │   └── ... (other models)
│   ├── routes/                         # Flask Blueprints for different parts of the API
│   │   ├── __init__.py
│   │   ├── auth_routes.py              # Authentication routes (if any beyond local)
│   │   ├── customer_routes.py
│   │   ├── appointment_routes.py
│   │   ├── product_routes.py
│   │   ├── service_routes.py
│   │   └── ... (other API route groups)
│   ├── services/                       # Business logic layer (optional, for complex operations)
│   │   ├── __init__.py
│   │   ├── notification_service.py
│   │   ├── report_service.py
│   │   └── backup_service.py
│   ├── static/                         # Static files served by Flask (rarely used when Electron is frontend)
│   ├── templates/                      # HTML templates (rarely used when Electron is frontend)
│   └── utils/                          # Utility functions and helpers
│       ├── __init__.py
│       └── helpers.py
│       └── validators.py
│
├── data/                               # Application data (user-generated content, database)
│   ├── salon_database.sqlite           # SQLite database file (primary recommended location)
│   ├── client_photos/                  # Directory for storing client photos
│   │   └── cust_101/
│   │       └── photo_before_20231115.jpg
│   │       └── photo_after_20231115.jpg
│   ├── db_backups/                     # Directory for database backups
│   │   └── backup_20231115_103000.sqlite.gz
│   ├── exported_reports/               # Directory for exported reports
│   │   └── financial_summary_2023_Q3.pdf
│   │   └── client_activity_2023_10.xlsx
│   └── logs/                           # Application logs (backend and/or frontend)
│       └── backend.log
│       └── electron_main.log
│
├── tests/                              # Automated tests
│   ├── backend/                        # Backend (Python) tests
│   │   ├── __init__.py
│   │   ├── conftest.py                 # Pytest fixtures and configuration
│   │   └── test_customer_routes.py
│   │   └── test_product_model.py
│   └── frontend/                       # Frontend (Electron/JavaScript) tests
│       ├── specs/
│       │   └── main_window_spec.js     # Example using Spectron or Playwright for Electron
│       └── unit/
│           └── renderer_utils_spec.js  # Unit tests for frontend JS modules
│
├── docs/                               # Project documentation
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── CORE_FUNCTIONALITIES.md
│   ├── API_INTEGRATION_PLAN.md
│   ├── PROJECT_STRUCTURE.md            # This file
│   └── setup_guide.md                  # Instructions for setting up the project
│
├── .gitignore                          # Specifies intentionally untracked files for Git
├── README.md                           # Main project README: overview, setup, how to run
└── package.json                        # Root package.json (optional, could manage both parts or just be for Electron build process)
                                        # This would contain scripts to run Electron, possibly start backend.
                                        # Its "main" field usually points to app/main.js or a similar root Electron entry.
```

**Explanation of Key Directories:**

*   **`app/`**: Contains all the code for the Electron frontend application.
    *   `main.js`: The entry point for Electron's main process. Responsible for creating browser windows, managing application lifecycle, and interacting with native OS features.
    *   `preload.js`: A script that runs before web page is loaded in the renderer process. It's used to securely expose specific Node.js/Electron APIs to the renderer process via `contextBridge` when `contextIsolation` is enabled.
    *   `index.html`: The main HTML file that forms the structure of the application's user interface.
    *   `styles/`: Contains CSS files for styling the UI.
    *   `scripts/`: Holds frontend JavaScript files.
        *   `renderer.js`: JavaScript that runs in the renderer process (the browser window), handling UI logic and interactions.
        *   `api_client.js` (Optional): A dedicated module for making requests to the Flask backend API, centralizing API call logic.
    *   `assets/`: Stores static assets like icons, images, or fonts used specifically by the UI.
    *   `package.json`: Node.js package file for the Electron app. Manages frontend dependencies (Electron, UI frameworks/libraries) and defines scripts for running, building, and packaging the Electron application.

*   **`backend/`**: Contains the Python/Flask backend API.
    *   `run.py` (or `app.py`): The main script to initialize and run the Flask application server.
    *   `config.py`: Stores configuration settings for the backend, such as the database connection string, secret keys for session management, paths for data storage, and external API keys.
    *   `requirements.txt`: Lists all Python package dependencies required for the backend (e.g., Flask, SQLAlchemy, requests).
    *   `instance/`: A Flask-specific folder (not usually version-controlled) for instance-specific configurations or files, like a local SQLite database file if not placed in the global `data/` directory, or override configuration files.
    *   `app_factory.py` (Optional but good practice): Contains an application factory function (e.g., `create_app()`) which is useful for creating multiple instances of the app (e.g., for testing) and for organizing initialization code.
    *   `models/`: Defines the structure of database tables, often using an ORM like SQLAlchemy or custom classes for direct database interaction. Each file typically represents a table.
    *   `routes/`: Organizes API endpoints. Each file typically defines a Flask Blueprint for a specific resource or functional area (e.g., `customer_routes.py` for all client-related API endpoints).
    *   `services/`: An optional layer for abstracting complex business logic away from the route handlers. Services can be called by multiple routes or other services.
    *   `utils/`: Contains utility functions, helper classes, or custom validators used across the backend.

*   **`data/`**: A dedicated top-level directory for all mutable application data generated and used by the system. This centralization simplifies backup and data management.
    *   `salon_database.sqlite`: The primary and recommended location for the SQLite database file.
    *   `client_photos/`: Directory for storing client-specific images (e.g., "before and after" photos), often organized into subdirectories per client.
    *   `db_backups/`: Default location for storing automated or manual backups of the SQLite database.
    *   `exported_reports/`: Default location for saving reports generated by the system (e.g., PDFs, Excel files).
    *   `logs/`: For storing log files generated by the backend or Electron main process, useful for debugging and monitoring.

*   **`tests/`**: Contains all automated tests.
    *   `backend/`: Tests for the Python/Flask backend (e.g., unit tests for models and services, integration tests for API endpoints using Pytest or unittest).
    *   `frontend/`: Tests for the Electron application (e.g., unit tests for JavaScript utility functions, end-to-end tests for UI interactions using tools like Spectron or Playwright).

*   **`docs/`**: Stores all project documentation files, including architectural diagrams, schema definitions, feature descriptions, and setup guides.

*   **`.gitignore`**: A standard Git file specifying intentionally untracked files and directories that Git should ignore (e.g., `__pycache__/`, `node_modules/`, `instance/`, `.env` files, log files, `data/salon_database.sqlite` if local dev DB shouldn't be committed).

*   **`README.md`**: The main project README file. It should provide an overview of the project, instructions for setting up the development environment, how to run the application, and other essential information for developers or users.

*   **`package.json` (Root Level - Optional):**
    A `package.json` at the root level can be used to manage both the Electron app and potentially scripts to run the backend concurrently, especially during development. Its "main" field would typically point to `app/main.js` or a similar script that launches the Electron application. It might include scripts like `npm start` to launch both frontend and backend.

This structure aims to create a clean separation of concerns between the frontend, backend, and data, facilitating easier development, testing, and maintenance.

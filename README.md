# Salon Management System

## 1. Introduction

Welcome to the Salon Management System project! This document provides a comprehensive overview of the conceptual design for a desktop application aimed at small to medium-sized beauty salons. The primary goal is to create a robust, user-friendly system that operates fully offline, with key differentiators focusing on intelligent features, data security, and a customizable user experience. While initially designed for local use, the system architecture incorporates considerations for future extensibility, including potential cloud synchronization and external API integrations.

This project outlines the system's architecture, database schema, core functionalities, API integration strategies, and proposed project structure, serving as a blueprint for development.

## 2. Key Features (Diferenciadas)

The system is designed with the following core features:

*   **Backup Inteligente e Offline:** Automatic and manual backups of the SQLite database to user-defined local or external directories, ensuring data safety.
*   **Gestão de Fichas de Clientes com Histórico Visual:** Comprehensive client profiles with the ability to upload and associate "before and after" photos.
*   **Cálculo Personalizado de Serviços:** System-suggested service packages or discounts based on client history and preferences.
*   **Controle Avançado de Estoque:** Tracking product quantities, alerts for low stock, flagging items near expiry, and suggesting reorders.
*   **Modo Offline com Sincronização Posterior (Conceptual):** Fully offline core functionality with a plan for future data synchronization with a central server/API.
*   **Integração com Webcam ou Dispositivos Locais:** Direct client photo capture using the computer's webcam.
*   **Agendamento Inteligente:** System assistance in finding optimal appointment slots based on client preferences and salon schedule patterns.
*   **Interface Personalizável:** User-selectable themes (e.g., light/dark mode) and potential for other UI customizations.
*   **Exportação de Relatórios em Formatos Variados:** Generation of reports (client flow, service performance, financials) in PDF, Excel, and interactive charts within the app.
*   **Módulo de Fidelização de Clientes:** A points-based loyalty program to reward and retain clients.

## 3. Overall Architecture
(Content from `docs/ARCHITECTURE.md`)

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

## 4. Interaction Diagram
(Content from `skeletons/interaction_diagram.md`)

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

## 5. Database Schema
(Content from `docs/DATABASE_SCHEMA.md`)

# Database Schema for Salon Management System

This document outlines the conceptual database schema for the salon management system, designed for use with SQLite. The actual implementation would involve `CREATE TABLE` SQL statements based on this schema. Timestamps are generally stored as ISO8601 strings.

## Tables

### 1. `Customers` Table
Stores information about clients.

*   `id` (INTEGER, Primary Key, Auto-increment)
*   `name` (TEXT, Not Null)
*   `phone` (TEXT, Unique)
*   `email` (TEXT, Unique)
*   `address` (TEXT)
*   `notes` (TEXT) - General notes about the client
*   `created_at` (TEXT, ISO8601 datetime)
*   `updated_at` (TEXT, ISO8601 datetime)

### 2. `ClientPhotos` Table
Stores paths to photos related to clients (e.g., before/after shots).

*   `id` (INTEGER, Primary Key, Auto-increment)
*   `customer_id` (INTEGER, Foreign Key referencing `Customers.id`)
*   `photo_type` (TEXT - e.g., 'before', 'after', 'general')
*   `image_path` (TEXT, Not Null) - Path to the locally stored image file
*   `description` (TEXT)
*   `uploaded_at` (TEXT, ISO8601 datetime)

### 3. `Services` Table
Defines the services offered by the salon.

*   `id` (INTEGER, Primary Key, Auto-increment)
*   `name` (TEXT, Not Null, Unique)
*   `description` (TEXT)
*   `price` (REAL, Not Null)
*   `duration_minutes` (INTEGER) - Estimated duration of the service
*   `category` (TEXT - e.g., 'Hair', 'Nails', 'Skincare')
*   `is_active` (INTEGER, Boolean, Default 1) - To deactivate services instead of deleting

### 4. `Appointments` Table
Manages appointments for customers and services.

*   `id` (INTEGER, Primary Key, Auto-increment)
*   `customer_id` (INTEGER, Foreign Key referencing `Customers.id`)
*   `service_id` (INTEGER, Foreign Key referencing `Services.id`) - Can be nullable if an appointment can be booked without immediate service selection, or a linking table could be used for multiple services per appointment. For simplicity, this schema starts with one service per appointment.
*   `appointment_datetime` (TEXT, ISO8601 datetime, Not Null)
*   `status` (TEXT - e.g., 'Scheduled', 'Completed', 'Cancelled', 'No-Show')
*   `notes` (TEXT) - Notes specific to this appointment
*   `price_at_booking` (REAL) - Price of the service at the time of booking
*   `created_at` (TEXT, ISO8601 datetime)
*   `updated_at` (TEXT, ISO8601 datetime)

### 5. `Products` Table (Inventory)
Tracks salon inventory (retail products, professional supplies).

*   `id` (INTEGER, Primary Key, Auto-increment)
*   `name` (TEXT, Not Null, Unique)
*   `brand` (TEXT)
*   `description` (TEXT)
*   `sku` (TEXT, Unique) - Stock Keeping Unit
*   `supplier` (TEXT)
*   `purchase_price` (REAL)
*   `sale_price` (REAL)
*   `quantity_on_hand` (INTEGER, Not Null, Default 0)
*   `reorder_level` (INTEGER, Default 0) - Alert when quantity falls below this level
*   `expiry_date` (TEXT, ISO8601 date) - For products with expiration
*   `last_stocked_date` (TEXT, ISO8601 datetime)
*   `created_at` (TEXT, ISO8601 datetime)
*   `updated_at` (TEXT, ISO8601 datetime)

### 6. `ProductUsage` Table
Links products to services (professional use) or direct sales.

*   `id` (INTEGER, Primary Key, Auto-increment)
*   `appointment_id` (INTEGER, Foreign Key referencing `Appointments.id`, Nullable if product sold directly and not part of a service in an appointment)
*   `product_id` (INTEGER, Foreign Key referencing `Products.id`)
*   `quantity_used` (INTEGER, Not Null)
*   `sale_id` (INTEGER, Nullable, could link to a future direct sales/transactions table if needed for sales outside appointments)
*   `usage_timestamp` (TEXT, ISO8601 datetime)

### 7. `ServicePackages` Table
Allows bundling multiple services into packages, possibly at a discounted price.

*   `id` (INTEGER, Primary Key, Auto-increment)
*   `name` (TEXT, Not Null)
*   `description` (TEXT)
*   `total_price` (REAL, Not Null)
*   `is_active` (INTEGER, Boolean, Default 1)

### 8. `ServicePackageItems` Table
A linking table that defines which services are part of which package.

*   `package_id` (INTEGER, Foreign Key referencing `ServicePackages.id`)
*   `service_id` (INTEGER, Foreign Key referencing `Services.id`)
*   `quantity` (INTEGER, Default 1) - How many times this service is included in the package
*   PRIMARY KEY (`package_id`, `service_id`)

### 9. `CustomerLoyalty` Table
Tracks customer loyalty points or status.

*   `customer_id` (INTEGER, Primary Key, Foreign Key referencing `Customers.id`)
*   `points` (INTEGER, Default 0)
*   `last_updated` (TEXT, ISO8601 datetime)

### 10. `AppSettings` Table
A key-value store for application-level settings (e.g., theme, backup preferences).

*   `key` (TEXT, Primary Key, Unique - e.g., 'theme_preference', 'backup_location', 'currency_symbol')
*   `value` (TEXT)

### 11. `Backups` Table
Stores metadata about database backups.

*   `id` (INTEGER, Primary Key, Auto-increment)
*   `backup_timestamp` (TEXT, ISO8601 datetime, Not Null)
*   `backup_path` (TEXT, Not Null) - Path to the backup file/directory
*   `status` (TEXT - e.g., 'Success', 'Failed', 'In Progress')
*   `notes` (TEXT) - Any notes regarding the backup, e.g., manual backup, automatic.

This schema provides a comprehensive starting point for the salon management system. Relationships are indicated by Foreign Key constraints. Data types are SQLite compatible. `TEXT` is used for dates/datetimes, assuming they will be stored in ISO8601 format for easy sorting and universal compatibility. Boolean values are represented as `INTEGER` (0 for false, 1 for true).

## 6. Conceptual Design of Core Functionalities
(Content from `docs/CORE_FUNCTIONALITIES.md`)

# Core Functionalities Conceptual Design

This document details the conceptual design for the core functionalities of the Salon Management System. For each functionality, it provides an overview, interaction with the defined architecture (Electron, Flask, SQLite), and the relevant database tables involved (as per `DATABASE_SCHEMA.md`).

---

### 1. Backup Inteligente e Offline

*   **Overview:**
    The system will provide both automatic and manual backup capabilities for the SQLite database file. Users will be able to define a preferred local or external directory for storing these backups. Automatic backups can be scheduled (e.g., daily, weekly).
*   **Interaction:**
    *   **Electron Frontend:** Provides a user interface for configuring the backup path, setting up the backup schedule (e.g., frequency, time), and initiating manual backups. It will also display the status of past backups.
    *   **Flask Backend:** An API endpoint (e.g., `/api/backups/trigger`) will exist to initiate a backup process. For scheduled backups, a simple scheduler (e.g., using Python's `schedule` library or `APScheduler`) running within the Flask application process will trigger the backup logic. Alternatively, the Electron main process could manage scheduling if direct system-level task scheduling is preferred. The backup process involves copying the main SQLite database file to the specified backup location with a timestamped name.
*   **Database:**
    *   `Backups`: This table will log each backup event, storing its timestamp, the path to the backup file, the status (Success/Failed), and any relevant notes (e.g., manual backup, scheduled backup).
    *   `AppSettings`: This table can store user-defined settings such as the default backup path and preferred backup schedule (e.g., `backup_path: /path/to/backups`, `backup_schedule: daily@02:00`).

---

### 2. Gestão de Fichas de Clientes com Histórico Visual

*   **Overview:**
    The system will maintain comprehensive profiles for each client, including contact details, preferences, and notes. A key feature is the ability to upload and associate "before and after" photos with client profiles, providing a visual history of services.
*   **Interaction:**
    *   **Electron Frontend:** Users can create, view, edit, and delete client profiles. An interface will allow users to select and upload images (e.g., JPG, PNG) from their computer. These images will be displayed within the client's profile, possibly in a gallery view, categorized by type (before, after, general).
    *   **Flask Backend:** Provides API endpoints for CRUD operations on client data (e.g., `/api/customers`, `/api/customers/<id>`). For image uploads, an endpoint (e.g., `/api/customers/<id>/photos`) will receive the image file. The backend will save the image to a designated, secure local folder (e.g., `data/client_images/<customer_id>/<image_name>`) and store the relative path or full path (if configurable) in the database.
*   **Database:**
    *   `Customers`: Stores all textual information for clients (name, phone, email, notes, etc.).
    *   `ClientPhotos`: Stores metadata for each photo, including a foreign key `customer_id` linking it to the `Customers` table, the `image_path` (path to the stored file), `photo_type`, description, and upload timestamp.

---

### 3. Cálculo Personalizado de Serviços

*   **Overview:**
    The system aims to provide personalized service suggestions or apply discounts by analyzing a client's history, such as their frequency of visits and the types of services previously availed. This could manifest as suggesting package deals or loyalty-based discounts.
*   **Interaction:**
    *   **Electron Frontend:** When booking a new appointment or viewing a client's profile, the frontend can request personalized suggestions from the backend. These suggestions would then be displayed to the user.
    *   **Flask Backend:** The backend will house the logic for this feature. An API endpoint (e.g., `/api/customers/<id>/service_suggestions`) will trigger the analysis. The logic will query the database for the client's appointment history, services used, and potentially their loyalty status. Based on predefined rules or simple machine learning models (future enhancement), it will identify patterns (e.g., client frequently gets service A and B together) or eligibility for existing packages/discounts.
*   **Database:**
    *   `Customers`: To identify the client.
    *   `Appointments`: To analyze historical appointment data (dates, services chosen, status).
    *   `Services`: To get details about services availed.
    *   `ServicePackages` & `ServicePackageItems`: To identify available packages that might be relevant or for which the client might be eligible.
    *   `CustomerLoyalty`: To factor in loyalty points or status for potential discounts.

---

### 4. Controle Avançado de Estoque

*   **Overview:**
    This feature will manage the salon's product inventory, tracking quantities on hand, alerting staff when stock levels are low (below a defined reorder level), flagging items nearing their expiry date, and potentially suggesting reorder quantities based on historical consumption rates.
*   **Interaction:**
    *   **Electron Frontend:** Provides an interface for viewing current stock levels, adding new products, updating product details (including purchase/sale price, SKU, quantity), and manually adjusting stock quantities (e.g., after a stock count). It will display alerts for low stock or near-expiry items.
    *   **Flask Backend:** Implements CRUD API endpoints for products (e.g., `/api/products`). It handles the logic for updating `quantity_on_hand` when products are used (linked via `ProductUsage`) or sold. A background task (scheduled within Flask or via Electron main process) could periodically scan the `Products` table to identify items needing reordering or nearing expiry and generate notifications (which could be stored or pushed to the frontend).
*   **Database:**
    *   `Products`: The primary table, storing product details, `quantity_on_hand`, `reorder_level`, `expiry_date`, `purchase_price`, `sale_price`.
    *   `ProductUsage`: Tracks how products are consumed (e.g., during appointments), allowing the system to calculate consumption rates for reorder suggestions.

---

### 5. Modo Offline com Sincronização Posterior (Conceptual)

*   **Overview:**
    The core application is designed to operate fully offline, with all data stored locally. For future expansion involving a cloud-based component or multi-device access, a synchronization mechanism will be needed. Changes made offline would be logged and synced to a central server/API when internet connectivity is restored.
*   **Interaction:**
    *   **Local Operations:** All current interactions (Electron frontend -> Flask backend -> SQLite database) function entirely offline.
    *   **Synchronization Logic (Future):**
        *   **Flask Backend:** A dedicated module within Flask would manage synchronization. It would identify local changes not yet synced (e.g., by checking `last_modified_timestamp` and a `sync_status` column in relevant tables). Upon detecting internet connectivity, it would attempt to send these changes to a predefined external API. It would also fetch changes from the server and apply them locally, handling potential conflicts.
        *   **Electron Frontend:** Might provide UI elements to show sync status, initiate manual sync, and resolve conflicts if necessary.
*   **Database (Conceptual for Sync):**
    *   Most transactional tables (e.g., `Customers`, `Appointments`, `Products`, `Services`) would need additional columns:
        *   `last_modified_timestamp` (TEXT, ISO8601 datetime): Updated whenever a record is changed.
        *   `sync_status` (TEXT - e.g., 'pending_sync', 'synced', 'conflict'): To track the state of each record relative to the central server.
        *   `global_id` (TEXT, UUID): A globally unique identifier for records that need to be synced across devices/databases, separate from the local auto-incrementing `id`.
    *   `SyncLog` (Table): Could be created to log synchronization attempts, their success/failure, timestamps, and number of records synced.

---

### 6. Integração com Webcam ou Dispositivos Locais

*   **Overview:**
    The system will allow users to capture client photos directly using the computer's built-in or connected webcam, streamlining the process of adding images to client profiles.
*   **Interaction:**
    *   **Electron Renderer Process:** Within the client management interface, JavaScript running in the renderer process will use web standard APIs like `navigator.mediaDevices.getUserMedia()` to request access to the webcam and display the live feed in an HTML element (e.g., `<video>`). Users can then capture a still image (e.g., drawn to an HTML `<canvas>` and converted to a data URL or Blob).
    *   **Flask Backend:** The captured image data is sent from the Electron frontend to a specific API endpoint on the Flask backend (similar to the file upload in functionality 2, e.g., `/api/customers/<id>/photos/capture`). The backend then saves this image data as a file in the designated client images folder and creates a corresponding record in the `ClientPhotos` table.
*   **Database:**
    *   `ClientPhotos`: Stores the path and metadata of the captured photo, linked to the relevant `customer_id`.

---

### 7. Agendamento Inteligente

*   **Overview:**
    The system will assist in scheduling by learning client preferences for appointment times and identifying busy or idle periods for the salon. This helps in suggesting optimal appointment slots to clients or for staff planning.
*   **Interaction:**
    *   **Electron Frontend:** When a user is creating a new appointment, the frontend can request scheduling suggestions from the backend. These suggestions (e.g., "Client X often books on Friday afternoons," or "Salon is usually quiet on Tuesday mornings") can be displayed to guide the booking process.
    *   **Flask Backend:** An API endpoint (e.g., `/api/appointments/suggestions`) will trigger the analysis. The backend logic will query the `Appointments` table to analyze historical data, looking for patterns related to specific clients (e.g., preferred days/times), services (e.g., popular times for long services), or overall salon traffic. Simple heuristics or statistical analysis can be used initially.
*   **Database:**
    *   `Appointments`: Primary source for historical data on appointment times, dates, services, and client linkage.
    *   `Services`: To understand the duration and type of services being scheduled.
    *   `Customers`: To link appointments back to specific client preferences if patterns are client-specific.

---

### 8. Interface Personalizável

*   **Overview:**
    Users will be able to personalize the application's appearance, for example, by choosing between a light or dark theme. Other UI customizations could be added in the future.
*   **Interaction:**
    *   **Electron Frontend:** The frontend will provide UI elements (e.g., a settings menu) to select themes. JavaScript will apply the selected theme by changing CSS styles, potentially using CSS custom properties (variables) or by swapping stylesheets. The chosen preference will be saved.
    *   **Persistence:**
        *   **Local Storage (Electron):** For instant application, the theme preference can be stored in Electron's `localStorage`.
        *   **Flask Backend (`AppSettings`):** For persistence across sessions or if settings need to be managed more centrally, the preference can be sent to a Flask API endpoint (e.g., `/api/settings`) and stored in the `AppSettings` table. On application startup, the frontend would fetch this setting.
*   **Database:**
    *   `AppSettings`: Used to store the user's theme preference (e.g., `key: 'ui_theme', value: 'dark'`) and potentially other customizable UI settings.

---

### 9. Exportação de Relatórios em Formatos Variados

*   **Overview:**
    The system will enable users to generate various reports, such as client flow analysis, service performance metrics, inventory status, and basic financial summaries. These reports should be exportable in common formats like PDF and Excel. Interactive charts could also be displayed within the application.
*   **Interaction:**
    *   **Electron Frontend:** Users will select the type of report they want to generate and specify any parameters (e.g., date ranges, specific clients or services). For interactive charts, the frontend will use a charting library (e.g., Chart.js, D3.js) to render visualizations based on data fetched from the backend. For file exports, the frontend will make a request to the backend.
    *   **Flask Backend:** API endpoints (e.g., `/api/reports/<report_type>`) will handle report generation. The backend will:
        1.  Query the relevant database tables based on the report type and parameters.
        2.  Aggregate and process the data.
        3.  Use Python libraries (e.g., `ReportLab` or `FPDF` for PDF; `openpyxl` or `XlsxWriter` for Excel) to generate the report file.
        4.  The generated file can then be sent back to the Electron frontend as a download or saved to a temporary location for the user to access.
*   **Database:**
    *   Potentially all tables, depending on the report. Examples:
        *   `Appointments`, `Customers`, `Services`: For client flow, service popularity, revenue per service.
        *   `Products`, `ProductUsage`: For inventory reports, stock valuation, consumption rates.
        *   `CustomerLoyalty`: For loyalty program status reports.

---

### 10. Módulo de Fidelização de Clientes

*   **Overview:**
    A points-based loyalty program will be implemented to reward repeat customers. Clients earn points for services availed or products purchased, and these points can be redeemed for discounts or specific rewards.
*   **Interaction:**
    *   **Electron Frontend:** Client profiles will display their current loyalty points. During checkout or appointment completion, the system will show points earned. An interface may allow viewing available rewards and redeeming points.
    *   **Flask Backend:**
        *   API endpoints will manage loyalty points (e.g., `/api/customers/<id>/loyalty`).
        *   After an appointment is marked 'Completed' or a sale is processed, the backend logic will calculate and add points to the `CustomerLoyalty` table for the respective client based on configurable rules (e.g., 1 point per $10 spent).
        *   Logic will also handle point redemption, deducting points when a reward is claimed.
*   **Database:**
    *   `CustomerLoyalty`: Stores the current point balance for each customer (`customer_id`, `points`, `last_updated`).
    *   `Services` / `Products`: May need a flag or separate fields to indicate if they are eligible for earning points or if they can be redeemed as rewards.
    *   A dedicated `Rewards` table could be introduced if rewards are more complex than simple discounts (e.g., "Free Product X for 500 points").
    *   `Appointments`: Data from this table (e.g., price of services) will be used to calculate points earned.

---

## 7. Future API Integration Plan
(Content from `docs/API_INTEGRATION_PLAN.md`)

# API Integration Plan

This document outlines the strategy for future API integrations with the Salon Management System. While the initial focus is a fully offline local application, this plan details how external services can be incorporated as the system evolves.

## 1. Backend API Design (Flask)

The Flask backend is architected to facilitate both internal (Electron frontend to Flask backend) and potential future external communications.

*   **RESTful Endpoints:**
    The core design philosophy is that the Flask application exposes its functionalities through RESTful API endpoints. These are already in use for communication between the Electron frontend and the Flask backend (e.g., `GET /api/clients`, `POST /api/appointments`). This API-centric approach simplifies adding new integrations.

*   **Modularity (Blueprints):**
    To maintain a clean and organized codebase, Flask Blueprints should be utilized. Each major functionality domain (e.g., clients, appointments, inventory) and each future external API integration (e.g., payments, notifications) can be organized into its own Blueprint. This modularity makes it easier to develop, test, and maintain different parts of the API.

*   **Authentication/Authorization for External Access (Future Consideration):**
    Currently, the Flask API is intended for local consumption by the Electron application (listening on `localhost`). If, in the future, any part of this API needs to be exposed to the internet or other services directly, robust authentication and authorization mechanisms would be paramount. This could involve:
    *   **API Keys:** For server-to-server communication.
    *   **OAuth2:** For granting third-party applications or users delegated access.
    *   **JWT (JSON Web Tokens):** For stateless session management.
    For the current local model, these are not strictly necessary but designing the API with distinct, secure endpoints is good practice.

## 2. Types of Future API Integrations & Strategy

The following are potential areas for API integration, along with strategies for their implementation:

### a. Payment Gateways (e.g., Stripe, PayPal, Pix)

*   **Strategy:** To maintain PCI compliance and security, direct handling of sensitive payment information by the Electron frontend should be minimized. The typical flow would involve the Flask backend acting as an intermediary between the Electron app and the payment gateway's API.
*   **Example Endpoint (Conceptual in Flask):** `POST /api/payments/process`
*   **Data Flow:**
    1.  **Electron Frontend:** Collects non-sensitive billing information or uses the payment gateway's client-side SDK/elements to tokenize payment details.
    2.  The frontend sends a request to the Flask backend endpoint (e.g., with the tokenized payment info or order details).
    3.  **Flask Backend:** Securely communicates server-to-server with the chosen payment gateway's API, sending the payment details and amount. Sensitive API keys for the payment gateway are stored and used only on the backend.
    4.  **Payment Gateway:** Processes the payment and returns a response (success/failure) to Flask.
    5.  **Flask Backend:** Updates the local SQLite database (e.g., marks an appointment as 'Paid', records the transaction).
    6.  Flask returns a confirmation or error message to the Electron frontend.

### b. Notification Services (e.g., Twilio for SMS, SendGrid/Mailgun for Email, Firebase Cloud Messaging for Push Notifications)

*   **Strategy:** The Flask backend will directly integrate with the APIs of notification services. Triggers for notifications (e.g., appointment reminders, marketing messages, low stock alerts) will originate from backend logic, often driven by scheduled tasks or specific events.
*   **Example Trigger (Conceptual in Flask):** A scheduled job checks for appointments occurring in 24 hours.
*   **Data Flow (SMS Reminder Example):**
    1.  A scheduler within Flask (e.g., APScheduler) triggers a function to find upcoming appointments.
    2.  For each due reminder, Flask constructs the message and uses the client's phone number from the `Customers` table.
    3.  Flask makes an API call to the SMS provider (e.g., Twilio) with the recipient's number and message content.
    4.  The SMS provider sends the message.
    5.  Flask logs the notification attempt (e.g., in a `NotificationsLog` table).

### c. Geolocation/Mapping Services (e.g., Google Maps API, OpenStreetMap)

*   **Strategy:** These services can enhance the UI by displaying client addresses on a map or providing directions.
*   **Interaction:**
    *   **Electron Frontend (Direct):** For simple map displays or geocoding, the Electron renderer process can directly use JavaScript client-side APIs provided by these services (e.g., embedding a Google Map). API keys, if required for client-side usage, would need careful management (e.g., restrictions to specific domains/referrers if possible, though less critical in a desktop app context).
    *   **Flask Backend (Indirect):** For more complex queries, route optimization, or if server-side processing of location data is needed, Flask can act as a proxy to these services.
*   **Example:** Displaying a client's address on a map in their profile within Electron.

### d. AI-Powered Suggestions (e.g., for product recommendations, service personalization, scheduling optimization)

*   **Strategy:** The Flask backend can leverage external AI/ML APIs to provide advanced insights or features. This involves sending relevant (potentially anonymized) data to an AI service and receiving processed results.
*   **Example (Service Personalization):**
    1.  **Electron Frontend:** User requests personalized service suggestions for a client.
    2.  Flask API endpoint is called.
    3.  **Flask Backend:** Gathers relevant client history (e.g., past services, frequency, stated preferences) from the local SQLite database.
    4.  Flask sends this data (potentially anonymized or aggregated) to an external AI service API (e.g., a custom model deployed on a cloud platform or a third-party AI service).
    5.  The AI service returns suggestions (e.g., list of recommended services, optimal booking times).
    6.  Flask processes these suggestions and relays them to the Electron frontend.

### e. Cloud Synchronization API (for the "Modo Offline com Sincronização Posterior")

*   **Strategy:** If the application evolves to support multi-device synchronization or a full cloud-hosted version, the local Flask application will act as a client to a central, custom-built cloud API. This cloud API would manage the canonical dataset.
*   **Local Flask App Endpoints (Conceptual, for interacting with the Cloud API):**
    *   `POST /api/sync/push-changes`: Sends locally created/updated/deleted records (identified by `sync_status` and `last_modified_timestamp`) to the central cloud API.
    *   `GET /api/sync/pull-changes`: Fetches changes (new or updated records) from the cloud API that are relevant to this local instance.
    *   Internal logic for conflict resolution (e.g., last-write-wins, or flagging for manual review).
*   **Data Flow:**
    1.  Local Flask app detects internet connectivity.
    2.  It calls its `push-changes` logic, which in turn calls the appropriate endpoint on the central cloud API.
    3.  It then calls its `pull-changes` logic, fetching data from the cloud API.
    4.  The Flask app merges the fetched data into the local SQLite database, updating `sync_status` and resolving conflicts.

## 3. Considerations for API Integration

Implementing external API integrations requires careful planning around several key aspects:

*   **Configuration Management:**
    *   **Secure Storage:** API keys, secrets, and other sensitive credentials for external services must be stored securely. Options include:
        *   Environment variables (loaded by Flask at startup).
        *   A dedicated configuration file (e.g., `.env`, `config.ini`) that is *not* committed to version control (added to `.gitignore`).
        *   For user-configurable API keys (e.g., for their own Twilio account), these could be stored encrypted in the `AppSettings` table or a local encrypted file.
*   **Error Handling & Resilience:**
    *   External API calls can fail due to network issues, service outages, or invalid requests.
    *   Implement robust error handling: timeouts, retries (with exponential backoff), circuit breaker patterns for frequently failing services.
    *   Provide graceful fallbacks or user feedback if an external service is temporarily unavailable.
*   **Asynchronous Operations:**
    *   Many API calls, especially those involving network I/O, can be time-consuming.
    *   To prevent blocking the Flask server (and thus the Electron frontend), use asynchronous operations for these calls:
        *   Python's `asyncio` and `aiohttp` for native async.
        *   For more complex background task management (especially if the application scales), consider integrating Celery with a message broker like Redis or RabbitMQ.
*   **Logging:**
    *   Implement detailed logging for all external API interactions.
    *   Log request parameters (masking sensitive data), response status codes, response bodies (if not too large), and any errors encountered. This is crucial for debugging integration issues.
*   **Rate Limiting & Quotas:**
    *   Be mindful of API rate limits and usage quotas imposed by third-party services.
    *   Implement client-side rate limiting in Flask if necessary to avoid exceeding these limits.
*   **Data Privacy and Compliance:**
    *   When sending data to external services, ensure compliance with relevant data privacy regulations (e.g., GDPR, LGPD).
    *   Only send the minimum necessary data. Anonymize or pseudonymize data where possible.
    *   Clearly inform users about the use of third-party services and obtain consent if required.

This plan provides a foundational strategy for extending the Salon Management System's capabilities through external API integrations, ensuring that such expansions are structured, secure, and maintainable.

## 8. Project Directory Structure
(Content from `docs/PROJECT_STRUCTURE.md`)

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

## 9. Technology Stack Summary

*   **Backend:** Python with Flask
*   **Frontend:** Electron.js (using HTML, CSS, JavaScript)
*   **Database:** SQLite

## 10. Setup and Running (Conceptual)

This section outlines the conceptual steps to set up and run the Salon Management System. Note that these are based on the conceptual design and skeleton files.

**Prerequisites:**

*   Python (3.8+ recommended) and Pip
*   Node.js (which includes npm) (LTS version recommended)

**Backend Setup (Flask):**

1.  Navigate to the `backend/` directory.
2.  Create a Python virtual environment: `python -m venv venv`
3.  Activate the virtual environment:
    *   Windows: `venv\Scripts\activate`
    *   macOS/Linux: `source venv/bin/activate`
4.  Install Python dependencies: `pip install -r requirements.txt` (The `requirements.txt` would list Flask, etc. The skeleton `backend_app_skeleton.py` only needs Flask and can be run directly if Flask is installed globally/locally).
5.  Run the backend server: `python run.py` (or `python backend_app_skeleton.py` if using the skeleton directly).
    *   The backend should start on `http://localhost:5001` (as per skeleton configuration).
    *   The first run of `backend_app_skeleton.py` will create a `salon_data.sqlite` file in the `data/` directory at the project root.

**Frontend Setup (Electron):**

1.  Navigate to the `app/` directory (or project root if `package.json` is there for Electron).
2.  Install Node.js dependencies: `npm install` (This would install Electron and any other frontend libraries defined in `app/package.json`).
3.  Start the Electron application: `npm start` (This command would typically be defined in `app/package.json` to run `electron .` or similar).
    *   Alternatively, if the Electron main script (`main.js` or `electron_main_skeleton.js`) is configured to manage the Flask backend, running the Electron app might also attempt to start the backend process.

**Using the Skeletons:**

The `skeletons/` directory contains illustrative code:
*   `backend_app_skeleton.py`: Can be run directly with Python (`python skeletons/backend_app_skeleton.py`) if Flask is installed. It's configured to create its SQLite database in `data/salon_data.sqlite` (relative to project root).
*   `electron_main_skeleton.js`: Can be launched with Electron (`electron skeletons/electron_main_skeleton.js` from the project root, assuming Electron is installed). It attempts to start the `backend_app_skeleton.py`.
*   `electron_index_skeleton.html` and `electron_renderer_skeleton.js`: Provide a basic UI that can interact with the backend skeleton. For these to work as intended with `electron_main_skeleton.js`, you'd need to:
    1.  Create an `app/` directory in the project root.
    2.  Copy `skeletons/electron_index_skeleton.html` to `app/index.html`.
    3.  Create `app/scripts/` and copy `skeletons/electron_renderer_skeleton.js` to `app/scripts/renderer.js`.
    4.  Create `app/styles/main.css` (can be empty).
    5.  Create a basic `app/preload.js` for IPC examples to function.
    6.  The `electron_main_skeleton.js` is already configured to look for these files in the `app/` directory from the project root.

**General Order of Operations for Development:**

1.  Start the Flask backend server.
2.  Start the Electron frontend application.

The Electron app will then make HTTP requests to the Flask backend to manage data.

## 11. Contributing

This project is currently a conceptual design and collection of planning documents and skeleton code. Contributions to expand upon this concept, develop the features, or refine the architecture would be welcome.

If you wish to contribute:

1.  Fork the repository (if applicable).
2.  Create a new branch for your feature or bug fix.
3.  Develop your changes, adhering to the proposed project structure and coding conventions (to be defined).
4.  Write tests for your changes.
5.  Submit a pull request for review.

---

This README provides a central point of reference for the Salon Management System's conceptual design. Refer to the detailed documents in the `docs/` directory for more specific information on each aspect of the project.

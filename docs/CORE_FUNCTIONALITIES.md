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

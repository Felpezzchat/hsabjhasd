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

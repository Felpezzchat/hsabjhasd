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

# backend/database.py
import sqlite3
import os
import click # For CLI commands
from flask import current_app, g 
from flask.cli import with_appcontext

def get_db_path():
    """Gets the database path from the current app config or constructs it if app context is not available."""
    if current_app:
        # This is the preferred way when app context is available
        return current_app.config['DATABASE_PATH']
    else:
        # Fallback for when app context is not available (e.g., running init-db directly from __main__)
        # Assumes this file (database.py) is in the 'backend' directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root_dir = os.path.dirname(backend_dir) # Moves up one level to project root
        return os.path.join(project_root_dir, 'data', 'salon_data.sqlite')

def get_db():
    """Connects to the application's configured database.
    The connection is unique for each request and will be reused if called again.
    """
    db_path = get_db_path()
    if 'db' not in g:
        # Ensure the data directory exists before connecting
        data_dir = os.path.dirname(db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"Created data directory: {data_dir}")
            
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES # For type detection
        )
        g.db.row_factory = sqlite3.Row # Access columns by name

    return g.db

def close_db(e=None):
    """Closes the database connection if it was opened."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db_schema():
    """Clears existing data and creates new tables based on DATABASE_SCHEMA.md."""
    db_path = get_db_path()
    # Ensure data directory exists, especially if called directly without app context
    data_dir = os.path.dirname(db_path)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")

    # Connect directly for initialization, not using g.db as it's for request context
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    # Drop tables in reverse order of creation due to foreign key constraints
    # (or use PRAGMA foreign_keys=OFF; ... PRAGMA foreign_keys=ON;)
    cursor.executescript('''
        PRAGMA writable_schema = 1;
        DELETE FROM sqlite_master WHERE type IN ('table', 'index', 'trigger');
        PRAGMA writable_schema = 0;
        VACUUM;
        PRAGMA integrity_check;
    ''')
    print("Cleared existing database objects (tables, indexes, triggers).")
    
    # Recreate tables based on DATABASE_SCHEMA.md
    cursor.execute('''
        CREATE TABLE Customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE,
            email TEXT UNIQUE,
            address TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE ClientPhotos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            photo_type TEXT, -- e.g., 'before', 'after', 'general'
            image_path TEXT NOT NULL,
            description TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES Customers (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE Services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            price REAL NOT NULL,
            duration_minutes INTEGER,
            category TEXT, -- e.g., 'Hair', 'Nails', 'Skincare'
            is_active INTEGER DEFAULT 1 -- Boolean (0 or 1)
        )
    ''')

    cursor.execute('''
        CREATE TABLE Appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            service_id INTEGER, -- For simplicity, one service. Could be a linking table for many.
            appointment_datetime TEXT NOT NULL, -- ISO8601
            status TEXT, -- e.g., 'Scheduled', 'Completed', 'Cancelled', 'No-Show'
            notes TEXT,
            price_at_booking REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES Customers (id) ON DELETE SET NULL,
            FOREIGN KEY (service_id) REFERENCES Services (id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            brand TEXT,
            description TEXT,
            sku TEXT UNIQUE,
            supplier TEXT,
            purchase_price REAL,
            sale_price REAL,
            quantity_on_hand INTEGER NOT NULL DEFAULT 0,
            reorder_level INTEGER DEFAULT 0,
            expiry_date TEXT, -- ISO8601 date
            last_stocked_date TEXT DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE ProductUsage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER, -- Link to appointment if used in a service
            product_id INTEGER NOT NULL,
            quantity_used INTEGER NOT NULL,
            sale_id INTEGER, -- Link to a direct sale if sold outside an appointment (future)
            usage_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES Appointments (id) ON DELETE SET NULL,
            FOREIGN KEY (product_id) REFERENCES Products (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE ServicePackages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            total_price REAL NOT NULL,
            is_active INTEGER DEFAULT 1 -- Boolean
        )
    ''')

    cursor.execute('''
        CREATE TABLE ServicePackageItems (
            package_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            PRIMARY KEY (package_id, service_id),
            FOREIGN KEY (package_id) REFERENCES ServicePackages (id) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES Services (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE CustomerLoyalty (
            customer_id INTEGER PRIMARY KEY,
            points INTEGER DEFAULT 0,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES Customers (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE AppSettings (
            key TEXT PRIMARY KEY UNIQUE NOT NULL,
            value TEXT
        )
    ''')
    # Add some default settings
    cursor.execute("INSERT INTO AppSettings (key, value) VALUES ('theme', 'light')")
    cursor.execute("INSERT INTO AppSettings (key, value) VALUES ('backup_path', '../data/db_backups')") # Adjusted path
    cursor.execute("INSERT INTO AppSettings (key, value) VALUES ('currency_symbol', '$')")

    cursor.execute('''
        CREATE TABLE Backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            backup_timestamp TEXT NOT NULL,
            backup_path TEXT NOT NULL,
            status TEXT, -- e.g., 'Success', 'Failed'
            notes TEXT
        )
    ''')

    db.commit()
    db.close()
    print(f"Database initialized/reset with full schema at {db_path}")

@click.command('init-db-schema') # Changed command name for clarity
@with_appcontext
def init_db_schema_command():
    """Clears existing data and creates new tables."""
    init_db_schema()
    click.echo('Initialized the database schema (all tables dropped and recreated).')

def init_app(app):
    """Register database functions with the Flask app. This is called by app.py."""
    app.teardown_appcontext(close_db) # Call close_db when the app context is popped
    app.cli.add_command(init_db_schema_command) # Add the new command to the CLI

if __name__ == '__main__':
    # This allows running 'python backend/database.py' directly to initialize the DB
    # Useful for development before Flask app is fully running or if app context is tricky.
    print("Initializing database schema directly (outside Flask app context)...")
    # Construct the path as Flask app would, relative to this file's location.
    # This assumes this file (database.py) is in 'backend'.
    # And 'data' directory is one level up from 'backend'.
    db_path_manual = get_db_path() # Uses the fallback in get_db_path
    print(f"Target database path for direct initialization: {db_path_manual}")
    
    # Ensure directory for db_path_manual exists
    manual_data_dir = os.path.dirname(db_path_manual)
    if not os.path.exists(manual_data_dir):
        os.makedirs(manual_data_dir)
        print(f"Created data directory: {manual_data_dir}")
        
    init_db_schema() # This function now uses get_db_path which has a fallback.
    print("Direct database schema initialization complete.")

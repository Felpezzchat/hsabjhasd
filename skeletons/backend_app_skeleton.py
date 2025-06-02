from flask import Flask, jsonify, request
import sqlite3 # Added for basic DB interaction
import os

app = Flask(__name__)

# Configuration
# Determine the absolute path for the data directory and database file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATABASE_PATH = os.path.join(DATA_DIR, 'salon_data.sqlite')

app.config['DATABASE_PATH'] = DATABASE_PATH

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def init_db():
    """Initializes the database with a basic schema if it doesn't exist."""
    if not os.path.exists(app.config['DATABASE_PATH']) or os.path.getsize(app.config['DATABASE_PATH']) == 0:
        print(f"Initializing database at {app.config['DATABASE_PATH']}")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT
            )
        ''')
        # Add some initial data
        cursor.execute("INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)",
                       ('Jane Doe', 'jane.doe@example.com', '123-456-7890'))
        cursor.execute("INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)",
                       ('John Smith', 'john.smith@example.com', '098-765-4321'))
        conn.commit()
        conn.close()
        print("Database initialized with clients table and sample data.")
    else:
        print(f"Database at {app.config['DATABASE_PATH']} already exists.")


@app.route('/')
def home():
    return "Salon Management Backend is Running!"

@app.route('/api/clients', methods=['GET'])
def get_clients():
    conn = get_db_connection()
    clients_cursor = conn.execute('SELECT id, name, email, phone FROM clients').fetchall()
    conn.close()
    clients_list = [dict(row) for row in clients_cursor]
    return jsonify(clients_list)

@app.route('/api/clients', methods=['POST'])
def add_client():
    if not request.json or not 'name' in request.json:
        return jsonify({"error": "Missing name in request body"}), 400

    new_client_data = request.json
    name = new_client_data['name']
    email = new_client_data.get('email')
    phone = new_client_data.get('phone')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)",
                       (name, email, phone))
        conn.commit()
        new_client_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": "Failed to add client (e.g., email already exists)", "details": str(e)}), 409
    finally:
        if conn: # Ensure connection is closed if error happened before new_client_id was set
            conn.close()

    return jsonify({"id": new_client_id, "name": name, "email": email, "phone": phone}), 201


@app.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    conn = get_db_connection()
    client_cursor = conn.execute('SELECT id, name, email, phone FROM clients WHERE id = ?', (client_id,)).fetchone()
    conn.close()
    if client_cursor:
        return jsonify(dict(client_cursor))
    return jsonify({"error": "Client not found"}), 404

# Conceptual endpoint for future API integration (e.g., external service)
@app.route('/api/external/some-service', methods=['GET'])
def call_external_service():
    # Logic to call an external API would go here
    # For example:
    # api_key = app.config.get('EXTERNAL_API_KEY') # Store API keys in config.py or environment variables
    # try:
    #     response = requests.get(f"https://api.externalservice.com/data?key={api_key}", timeout=5)
    #     response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
    #     data = response.json()
    #     return jsonify({"message": "Conceptual external API call successful", "data": data})
    # except requests.exceptions.RequestException as e:
    #     return jsonify({"error": f"External API call failed: {str(e)}"}), 503
    return jsonify({"message": "Conceptual external API call", "data": {"info": "some data from external service"}})


if __name__ == '__main__':
    print(f"Base directory: {BASE_DIR}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Database path: {DATABASE_PATH}")
    init_db() # Initialize DB if it doesn't exist
    # Note: In a production Electron app, Flask would likely be started as a separate process
    # by the Electron main process.
    # For development, this can be run directly.
    # Ensure the port is different from Electron's default if it serves content directly.
    app.run(host='0.0.0.0', port=5001, debug=True) # Using port 5001 for Flask
    # Use `debug=False` in a production-like scenario if Flask is managed by Electron.
    # `debug=True` is useful for development as it enables auto-reloading.
    # `host='0.0.0.0'` makes it accessible from any IP, useful if Electron runs in a VM or container for dev.
    # `host='127.0.0.1'` (default) is fine for most local Electron setups.

    # To run this:
    # 1. Make sure Flask and other dependencies are installed: pip install Flask
    # 2. Navigate to the 'skeletons' directory.
    # 3. Run: python backend_app_skeleton.py
    # The backend will be available at http://localhost:5001
    # The database 'salon_data.sqlite' will be created in a 'data' directory
    # one level above the 'skeletons' directory (i.e., in the project root's 'data/' folder).
    # If you want it inside 'skeletons/data', change BASE_DIR to os.path.dirname(__file__)
    # and DATA_DIR to os.path.join(BASE_DIR, 'data_local_to_skeleton')
    # However, the project structure implies data is at the root.

    # Example of how the path is constructed:
    # __file__ (current file path) -> e.g., /path/to/project/skeletons/backend_app_skeleton.py
    # os.path.dirname(__file__) -> /path/to/project/skeletons
    # os.path.join(os.path.dirname(__file__), '..') -> /path/to/project
    # BASE_DIR -> /path/to/project
    # DATA_DIR -> /path/to/project/data
    # DATABASE_PATH -> /path/to/project/data/salon_data.sqlite
    # This matches the desired PROJECT_STRUCTURE.md

    # If this script is moved to backend/run.py as per project structure:
    # BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) would still point to project root.
    # DATA_DIR = os.path.join(BASE_DIR, 'data') would correctly point to project_root/data/
    # This pathing is robust to relocation of the script within the backend folder.
    # Alternatively, if backend/run.py is the entry point, and backend/instance/ is used for DB:
    # INSTANCE_DIR = os.path.join(os.path.dirname(__file__), 'instance')
    # DATABASE_PATH = os.path.join(INSTANCE_DIR, 'salon_data.sqlite')
    # app.config['INSTANCE_PATH'] = INSTANCE_DIR
    # This version uses the /data directory as per the main project structure.
print("Script loaded. If not running via __main__, Flask app object is now defined.")

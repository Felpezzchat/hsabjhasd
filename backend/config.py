import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__)) # backend directory
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..')) # Project root directory
DATA_DIR = os.path.join(PROJECT_ROOT, 'data') # Project_root/data/

# Ensure DATA_DIR exists
if not os.path.exists(DATA_DIR):
    print(f"Data directory not found at {DATA_DIR}. Creating it.")
    os.makedirs(DATA_DIR)
else:
    print(f"Data directory already exists at {DATA_DIR}.")

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-that-should-be-changed'
    
    # Database path configuration
    DATABASE_PATH = os.path.join(DATA_DIR, 'salon_data.sqlite')
    
    DEBUG = True # Set to False in production for a real application
    
    # Upload folder for client images
    UPLOAD_FOLDER = os.path.join(DATA_DIR, 'client_images') 
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Ensure UPLOAD_FOLDER exists upon config load
    if not os.path.exists(UPLOAD_FOLDER):
        print(f"Upload folder not found at {UPLOAD_FOLDER}. Creating it.")
        os.makedirs(UPLOAD_FOLDER)
    else:
        print(f"Upload folder already exists at {UPLOAD_FOLDER}.")

    # Example for future API keys, loaded from environment variables if set
    # EXTERNAL_API_KEY = os.environ.get('EXTERNAL_API_KEY')

    # Flask specific configurations can be added here, e.g.
    # SQLALCHEMY_TRACK_MODIFICATIONS = False # If using SQLAlchemy
    # JSON_SORT_KEYS = False # To preserve order of keys in JSON responses

    print(f"Config Initialized: DATABASE_PATH set to {DATABASE_PATH}")
    print(f"Config Initialized: UPLOAD_FOLDER set to {UPLOAD_FOLDER}")

# To verify paths during development:
# print(f"Config.py: BASE_DIR (backend) = {BASE_DIR}")
# print(f"Config.py: PROJECT_ROOT = {PROJECT_ROOT}")
# print(f"Config.py: DATA_DIR = {DATA_DIR}")
# print(f"Config.py: Config.DATABASE_PATH = {Config.DATABASE_PATH}")
# print(f"Config.py: Config.UPLOAD_FOLDER = {Config.UPLOAD_FOLDER}")

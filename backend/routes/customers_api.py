# backend/routes/customers_api.py
import sqlite3
from flask import Blueprint, request, jsonify, current_app, url_for
from backend.database import get_db
import os
from werkzeug.utils import secure_filename
import uuid # For generating unique filenames

customers_bp = Blueprint('customers_bp', __name__, url_prefix='/api/clients')

# --- Standard Client CRUD ---
@customers_bp.route('', methods=['GET'])
def get_clients():
    # ... (existing get_clients implementation) ...
    current_app.logger.info("GET /api/clients called")
    db = get_db()
    try:
        cursor = db.execute('SELECT * FROM Customers ORDER BY name')
        clients_rows = cursor.fetchall()
        clients_list = [dict(row) for row in clients_rows]
        return jsonify(clients_list), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching clients: {e}")
        return jsonify({"error": "Failed to fetch clients", "details": str(e)}), 500

@customers_bp.route('', methods=['POST'])
def add_client():
    # ... (existing add_client implementation) ...
    current_app.logger.info(f"POST /api/clients called with data: {request.json}")
    if not request.json or not 'name' in request.json or not request.json['name'].strip():
        current_app.logger.warning("Add client: Name is a required field.")
        return jsonify({"error": "Name is a required field."}), 400
    
    data = request.json
    name = data['name'].strip()
    email = data.get('email').strip() if data.get('email') else None
    phone = data.get('phone').strip() if data.get('phone') else None
    address = data.get('address').strip() if data.get('address') else None
    notes = data.get('notes').strip() if data.get('notes') else None

    if email and '@' not in email: # Basic email validation
        current_app.logger.warning(f"Add client: Invalid email format for {email}")
        return jsonify({"error": "Invalid email format."}), 400

    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO Customers (name, email, phone, address, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)',
            (name, email, phone, address, notes)
        )
        db.commit()
        new_client_id = cursor.lastrowid
        client_cursor = db.execute('SELECT * FROM Customers WHERE id = ?', (new_client_id,))
        created_client = dict(client_cursor.fetchone())
        current_app.logger.info(f"Client '{name}' (ID: {new_client_id}) added successfully.")
        return jsonify(created_client), 201
    except sqlite3.IntegrityError as e:
        db.rollback()
        error_detail = str(e).lower()
        if email and 'unique constraint failed: customers.email' in error_detail:
             current_app.logger.warning(f"Add client: Email '{email}' already exists. Error: {e}")
             return jsonify({"error": f"Email '{email}' already exists."}), 409
        if phone and 'unique constraint failed: customers.phone' in error_detail:
             current_app.logger.warning(f"Add client: Phone '{phone}' already exists. Error: {e}")
             return jsonify({"error": f"Phone number '{phone}' already exists."}), 409
        current_app.logger.error(f"Integrity error adding client: {e}")
        return jsonify({"error": "Database integrity error. Email or phone may already exist.", "details": str(e)}), 409
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Unexpected error adding client: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@customers_bp.route('/<int:client_id>', methods=['GET'])
def get_client(client_id):
    # ... (existing get_client implementation) ...
    current_app.logger.info(f"GET /api/clients/{client_id} called")
    db = get_db()
    try:
        cursor = db.execute('SELECT * FROM Customers WHERE id = ?', (client_id,))
        client = cursor.fetchone()
        if client:
            return jsonify(dict(client)), 200
        current_app.logger.warning(f"GET /api/clients/{client_id}: Client not found.")
        return jsonify({"error": "Client not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching client {client_id}: {e}")
        return jsonify({"error": "Failed to fetch client details", "details": str(e)}), 500

@customers_bp.route('/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    # ... (existing update_client implementation) ...
    current_app.logger.info(f"PUT /api/clients/{client_id} called with data: {request.json}")
    if not request.json:
        current_app.logger.warning(f"Update client {client_id}: Invalid JSON.")
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email').strip() if data.get('email') else None
    phone = data.get('phone').strip() if data.get('phone') else None
    address = data.get('address').strip() if data.get('address') else None
    notes = data.get('notes').strip() if data.get('notes') else None

    if not name: 
        current_app.logger.warning(f"Update client {client_id}: Name cannot be empty.")
        return jsonify({"error": "Name cannot be empty"}), 400
    if email and '@' not in email: 
        current_app.logger.warning(f"Update client {client_id}: Invalid email format for {email}.")
        return jsonify({"error": "Invalid email format."}), 400
            
    db = get_db()
    try:
        check_cursor = db.execute('SELECT id FROM Customers WHERE id = ?', (client_id,))
        if not check_cursor.fetchone():
            current_app.logger.warning(f"Update client {client_id}: Client not found.")
            return jsonify({"error": "Client not found"}), 404

        db.execute(
            'UPDATE Customers SET name = ?, email = ?, phone = ?, address = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (name, email, phone, address, notes, client_id)
        )
        db.commit()
        updated_client_cursor = db.execute('SELECT * FROM Customers WHERE id = ?', (client_id,))
        updated_client = dict(updated_client_cursor.fetchone())
        current_app.logger.info(f"Client {client_id} updated successfully.")
        return jsonify(updated_client), 200
    except sqlite3.IntegrityError as e:
        db.rollback()
        error_detail = str(e).lower()
        if email and 'unique constraint failed: customers.email' in error_detail:
            current_app.logger.warning(f"Update client {client_id}: Email '{email}' already exists. Error: {e}")
            return jsonify({"error": f"Email '{email}' already exists for another client."}), 409
        if phone and 'unique constraint failed: customers.phone' in error_detail:
            current_app.logger.warning(f"Update client {client_id}: Phone '{phone}' already exists. Error: {e}")
            return jsonify({"error": f"Phone number '{phone}' already exists for another client."}), 409
        current_app.logger.error(f"Integrity error updating client {client_id}: {e}")
        return jsonify({"error": "Database integrity error during update. Email or phone may already exist for another client.", "details": str(e)}), 409
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Unexpected error updating client {client_id}: {e}")
        return jsonify({"error": "An unexpected error occurred during update", "details": str(e)}), 500

@customers_bp.route('/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    # ... (existing delete_client implementation) ...
    current_app.logger.info(f"DELETE /api/clients/{client_id} called")
    db = get_db()
    try:
        check_cursor = db.execute('SELECT id FROM Customers WHERE id = ?', (client_id,))
        if not check_cursor.fetchone():
            current_app.logger.warning(f"Delete client {client_id}: Client not found.")
            return jsonify({"error": "Client not found"}), 404
                
        db.execute('DELETE FROM Customers WHERE id = ?', (client_id,)) # Related photos/loyalty will cascade delete
        db.commit()
        current_app.logger.info(f"Client {client_id} deleted successfully.")
        return jsonify({"message": "Client deleted successfully"}), 200
    except Exception as e:
        db.rollback() 
        current_app.logger.error(f"Error deleting client {client_id}: {e}")
        return jsonify({"error": "Failed to delete client", "details": str(e)}), 500

# --- Client Photo Management ---

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@customers_bp.route('/<int:client_id>/photos', methods=['POST'])
def upload_client_photo(client_id):
    current_app.logger.info(f"POST /api/clients/{client_id}/photos called")
    db = get_db()
    client_cursor = db.execute('SELECT id FROM Customers WHERE id = ?', (client_id,))
    if not client_cursor.fetchone():
        return jsonify({"error": "Client not found"}), 404

    if 'photo' not in request.files:
        return jsonify({"error": "No photo file part in request"}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    photo_type = request.form.get('photo_type', 'general')
    description = request.form.get('description', '').strip() or None

    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{extension}"
        
        # UPLOAD_FOLDER is absolute path from config
        client_upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(client_id))
        if not os.path.exists(client_upload_folder):
            try:
                os.makedirs(client_upload_folder)
                current_app.logger.info(f"Created client image subfolder: {client_upload_folder}")
            except OSError as e:
                current_app.logger.error(f"Error creating client image subfolder {client_upload_folder}: {e}")
                return jsonify({"error": "Failed to create directory for photo", "details": str(e)}), 500

        
        file_path_absolute = os.path.join(client_upload_folder, unique_filename)
        # Store path relative to UPLOAD_FOLDER in DB for portability and use with photo server
        file_path_relative = os.path.join(str(client_id), unique_filename) 

        try:
            file.save(file_path_absolute)
            current_app.logger.info(f"Photo saved to {file_path_absolute}")
            
            cursor = db.execute(
                'INSERT INTO ClientPhotos (customer_id, photo_type, image_path, description) VALUES (?, ?, ?, ?)',
                (client_id, photo_type, file_path_relative, description)
            )
            db.commit()
            new_photo_id = cursor.lastrowid
            
            # Fetch the newly created photo record to return it
            photo_data_cursor = db.execute('SELECT * FROM ClientPhotos WHERE id = ?', (new_photo_id,))
            new_photo_data = dict(photo_data_cursor.fetchone())
            
            # Add a dynamically generated URL for accessing the photo
            # This uses the 'photos_bp.serve_client_photo' endpoint defined in photo_server_api.py
            # Ensure photos_bp is registered in app.py before this can work.
            try:
                new_photo_data['image_url'] = url_for('photos_bp.serve_client_photo', filepath=new_photo_data['image_path'], _external=False)
            except Exception as url_e: # Catch potential RuntimeError if photos_bp not ready or outside app context
                current_app.logger.warning(f"Could not generate URL for photo: {url_e}. Client may need to construct it.")
                new_photo_data['image_url'] = f"/api/photos/{new_photo_data['image_path']}" # Fallback path

            return jsonify({"message": "Photo uploaded successfully", "photo": new_photo_data}), 201
        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Error saving photo or DB record: {e}")
            if os.path.exists(file_path_absolute): # Attempt to clean up saved file if DB error
                try:
                    os.remove(file_path_absolute)
                except OSError as ose:
                     current_app.logger.error(f"Error removing file {file_path_absolute} after DB error: {ose}")
            return jsonify({"error": "Failed to save photo", "details": str(e)}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400

@customers_bp.route('/<int:client_id>/photos', methods=['GET'])
def get_client_photos(client_id):
    current_app.logger.info(f"GET /api/clients/{client_id}/photos called")
    db = get_db()
    client_cursor = db.execute('SELECT id FROM Customers WHERE id = ?', (client_id,))
    if not client_cursor.fetchone():
        return jsonify({"error": "Client not found"}), 404
            
    try:
        cursor = db.execute('SELECT id, customer_id, photo_type, image_path, description, uploaded_at FROM ClientPhotos WHERE customer_id = ? ORDER BY uploaded_at DESC', (client_id,))
        photos_rows = cursor.fetchall()
        photos_list = []
        for row in photos_rows:
            photo_dict = dict(row)
            try:
                photo_dict['image_url'] = url_for('photos_bp.serve_client_photo', filepath=photo_dict['image_path'], _external=False)
            except Exception as url_e:
                current_app.logger.warning(f"Could not generate URL for photo {photo_dict['image_path']}: {url_e}")
                photo_dict['image_url'] = f"/api/photos/{photo_dict['image_path']}" # Fallback path
            photos_list.append(photo_dict)
        return jsonify(photos_list), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching photos for client {client_id}: {e}")
        return jsonify({"error": "Failed to fetch photos", "details": str(e)}), 500

@customers_bp.route('/photos/<int:photo_id>', methods=['DELETE'])
def delete_client_photo(photo_id):
    current_app.logger.info(f"DELETE /api/clients/photos/{photo_id} called")
    db = get_db()
    try:
        photo_cursor = db.execute('SELECT image_path FROM ClientPhotos WHERE id = ?', (photo_id,))
        photo_data = photo_cursor.fetchone()

        if not photo_data:
            return jsonify({"error": "Photo not found"}), 404

        relative_file_path = photo_data['image_path']
        # UPLOAD_FOLDER is absolute path
        absolute_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], relative_file_path)

        db.execute('DELETE FROM ClientPhotos WHERE id = ?', (photo_id,))
        db.commit() # Commit DB change first

        file_deleted_successfully = False
        if os.path.exists(absolute_file_path):
            try:
                os.remove(absolute_file_path)
                current_app.logger.info(f"Photo file {absolute_file_path} deleted.")
                file_deleted_successfully = True
                # Consider removing client subfolder if empty - can be complex, skip for now
            except OSError as e:
                current_app.logger.error(f"Error deleting photo file {absolute_file_path}: {e}")
                # DB record is deleted, but file is not. This is a partial success.
                return jsonify({"message": "Photo record deleted, but file system deletion failed.", "details": str(e)}), 207 # Multi-Status
        else:
            current_app.logger.warning(f"Photo file {absolute_file_path} not found for deletion, but DB record was removed.")
            # This might be okay if file was already manually removed or never existed.
            file_deleted_successfully = True # Treat as success from API perspective if file is already gone.

        return jsonify({"message": "Photo deleted successfully"}), 200
    except Exception as e:
        db.rollback() 
        current_app.logger.error(f"Error processing photo deletion for ID {photo_id}: {e}")
        return jsonify({"error": "Failed to delete photo", "details": str(e)}), 500

# backend/routes/services_api.py
import sqlite3
from flask import Blueprint, request, jsonify, current_app
from backend.database import get_db

services_bp = Blueprint('services_bp', __name__, url_prefix='/api/services')

@services_bp.route('', methods=['GET'])
def get_services():
    current_app.logger.info(f"GET /api/services called with args: {request.args}")
    db = get_db()
    try:
        # Filter by is_active by default, allow 'all' to get everything
        show_all = request.args.get('show_all', 'false').lower() == 'true'
        
        query = 'SELECT * FROM Services'
        if not show_all:
            query += ' WHERE is_active = 1'
        query += ' ORDER BY category, name' # Added category to sort order
        
        cursor = db.execute(query)
        services_rows = cursor.fetchall()
        services_list = [dict(row) for row in services_rows]
        return jsonify(services_list), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching services: {e}")
        return jsonify({"error": "Failed to fetch services", "details": str(e)}), 500

@services_bp.route('', methods=['POST'])
def add_service():
    current_app.logger.info(f"POST /api/services called with data: {request.json}")
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400
    
    data = request.json
    name = data.get('name', '').strip()
    price_str = data.get('price') # Keep as string for initial validation
    description = data.get('description', '').strip() or None
    duration_str = data.get('duration_minutes') # Keep as string for initial validation
    category = data.get('category', '').strip() or None
    is_active_val = data.get('is_active', 1) # Default to active (True/1)

    if not name:
        current_app.logger.warning("Add service: Name is required.")
        return jsonify({"error": "Service name is required."}), 400
    if price_str is None : # Must be provided
        current_app.logger.warning("Add service: Price is required.")
        return jsonify({"error": "Service price is required."}), 400
    
    try:
        price = float(price_str)
        if price < 0:
            current_app.logger.warning(f"Add service: Price cannot be negative ({price}).")
            return jsonify({"error": "Price cannot be negative."}), 400
    except (ValueError, TypeError):
        current_app.logger.warning(f"Add service: Invalid price format ('{price_str}').")
        return jsonify({"error": "Invalid price format. Must be a number."}), 400

    duration_minutes = None
    if duration_str is not None: # Optional field
        try:
            duration_minutes = int(duration_str)
            if duration_minutes < 0:
                current_app.logger.warning(f"Add service: Duration cannot be negative ({duration_minutes}).")
                return jsonify({"error": "Duration cannot be negative."}), 400
        except (ValueError, TypeError):
            current_app.logger.warning(f"Add service: Invalid duration format ('{duration_str}').")
            return jsonify({"error": "Invalid duration format. Must be an integer."}), 400
    
    is_active = 1 if is_active_val in [True, 1, '1', 'true'] else 0


    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO Services (name, description, price, duration_minutes, category, is_active) VALUES (?, ?, ?, ?, ?, ?)',
            (name, description, price, duration_minutes, category, is_active)
        )
        db.commit()
        new_service_id = cursor.lastrowid
        service_cursor = db.execute('SELECT * FROM Services WHERE id = ?', (new_service_id,))
        created_service = dict(service_cursor.fetchone())
        current_app.logger.info(f"Service '{name}' (ID: {new_service_id}) added successfully.")
        return jsonify(created_service), 201
    except sqlite3.IntegrityError as e:
        db.rollback()
        if 'unique constraint failed: services.name' in str(e).lower():
            current_app.logger.warning(f"Add service: Name '{name}' already exists. Error: {e}")
            return jsonify({"error": f"Service with name '{name}' already exists."}), 409
        current_app.logger.error(f"Integrity error adding service: {e}")
        return jsonify({"error": "Database integrity error. Service name may already exist.", "details": str(e)}), 409
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Unexpected error adding service: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@services_bp.route('/<int:service_id>', methods=['GET'])
def get_service(service_id):
    current_app.logger.info(f"GET /api/services/{service_id} called")
    db = get_db()
    try:
        cursor = db.execute('SELECT * FROM Services WHERE id = ?', (service_id,))
        service = cursor.fetchone()
        if service:
            return jsonify(dict(service)), 200
        current_app.logger.warning(f"GET /api/services/{service_id}: Service not found.")
        return jsonify({"error": "Service not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching service {service_id}: {e}")
        return jsonify({"error": "Failed to fetch service details", "details": str(e)}), 500

@services_bp.route('/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    current_app.logger.info(f"PUT /api/services/{service_id} called with data: {request.json}")
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.json
    
    db = get_db()
    try:
        current_service_cursor = db.execute('SELECT * FROM Services WHERE id = ?', (service_id,))
        current_service = current_service_cursor.fetchone()
        if not current_service:
            current_app.logger.warning(f"Update service {service_id}: Service not found.")
            return jsonify({"error": "Service not found"}), 404

        # Start with current values, then update with provided ones
        final_name = data.get('name', current_service['name']).strip()
        final_description = data.get('description', current_service['description'])
        if final_description is not None: final_description = final_description.strip()
        
        final_category = data.get('category', current_service['category'])
        if final_category is not None: final_category = final_category.strip()

        final_price = current_service['price']
        if 'price' in data:
            price_str = data.get('price')
            if price_str is None: # Explicitly setting price to null is not allowed
                return jsonify({"error": "Price cannot be null. Provide a valid number."}), 400
            try:
                final_price = float(price_str)
                if final_price < 0:
                    return jsonify({"error": "Price cannot be negative."}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid price format. Must be a number."}), 400
        
        final_duration = current_service['duration_minutes']
        if 'duration_minutes' in data:
            duration_str = data.get('duration_minutes')
            if duration_str is None: # Can set duration to null
                final_duration = None
            else:
                try:
                    final_duration = int(duration_str)
                    if final_duration < 0:
                        return jsonify({"error": "Duration cannot be negative."}), 400
                except (ValueError, TypeError):
                    return jsonify({"error": "Invalid duration format. Must be an integer."}), 400

        final_is_active = current_service['is_active']
        if 'is_active' in data:
            is_active_val = data.get('is_active')
            if is_active_val is None: # Explicitly setting is_active to null is not allowed
                 return jsonify({"error": "is_active cannot be null. Must be 0 or 1 (or boolean)."}), 400
            final_is_active = 1 if is_active_val in [True, 1, '1', 'true'] else 0


        if not final_name: # Name must not be empty after stripping
             current_app.logger.warning(f"Update service {service_id}: Name cannot be empty.")
             return jsonify({"error": "Service name cannot be empty"}), 400
        
        db.execute(
            'UPDATE Services SET name = ?, description = ?, price = ?, duration_minutes = ?, category = ?, is_active = ? WHERE id = ?',
            (final_name, final_description, final_price, final_duration, final_category, final_is_active, service_id)
        )
        db.commit()
        updated_service_cursor = db.execute('SELECT * FROM Services WHERE id = ?', (service_id,))
        updated_service = dict(updated_service_cursor.fetchone())
        current_app.logger.info(f"Service {service_id} updated successfully.")
        return jsonify(updated_service), 200
    except sqlite3.IntegrityError as e:
        db.rollback()
        if 'unique constraint failed: services.name' in str(e).lower():
            current_app.logger.warning(f"Update service {service_id}: Name '{final_name}' already exists. Error: {e}")
            return jsonify({"error": f"Service with name '{final_name}' already exists for another service."}), 409
        current_app.logger.error(f"Integrity error updating service {service_id}: {e}")
        return jsonify({"error": "Database integrity error during update. Service name may already exist.", "details": str(e)}), 409
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Unexpected error updating service {service_id}: {e}")
        return jsonify({"error": "An unexpected error occurred during update", "details": str(e)}), 500

@services_bp.route('/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    current_app.logger.info(f"DELETE /api/services/{service_id} called")
    # Note: Deleting a service might have implications for appointments.
    # The schema sets service_id in Appointments to NULL ON DELETE.
    db = get_db()
    try:
        check_cursor = db.execute('SELECT id FROM Services WHERE id = ?', (service_id,))
        if not check_cursor.fetchone():
            current_app.logger.warning(f"Delete service {service_id}: Service not found.")
            return jsonify({"error": "Service not found"}), 404
                
        db.execute('DELETE FROM Services WHERE id = ?', (service_id,))
        db.commit()
        current_app.logger.info(f"Service {service_id} deleted successfully.")
        return jsonify({"message": "Service deleted successfully"}), 200
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error deleting service {service_id}: {e}")
        return jsonify({"error": "Failed to delete service", "details": str(e)}), 500

@services_bp.route('/<int:service_id>/deactivate', methods=['POST'])
def deactivate_service(service_id):
    current_app.logger.info(f"POST /api/services/{service_id}/deactivate called")
    db = get_db()
    try:
        check_cursor = db.execute('SELECT id, is_active FROM Services WHERE id = ?', (service_id,))
        service = check_cursor.fetchone()
        if not service:
            current_app.logger.warning(f"Deactivate service {service_id}: Service not found.")
            return jsonify({"error": "Service not found"}), 404
        if service['is_active'] == 0:
            return jsonify({"message": "Service is already deactivated.", "service": dict(service)}), 200
            
        db.execute('UPDATE Services SET is_active = 0 WHERE id = ?', (service_id,))
        db.commit()
        updated_service_cursor = db.execute('SELECT * FROM Services WHERE id = ?', (service_id,))
        updated_service = dict(updated_service_cursor.fetchone())
        current_app.logger.info(f"Service {service_id} deactivated successfully.")
        return jsonify({"message": "Service deactivated successfully", "service": updated_service}), 200
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error deactivating service {service_id}: {e}")
        return jsonify({"error": "Failed to deactivate service", "details": str(e)}), 500

@services_bp.route('/<int:service_id>/activate', methods=['POST'])
def activate_service(service_id):
    current_app.logger.info(f"POST /api/services/{service_id}/activate called")
    db = get_db()
    try:
        check_cursor = db.execute('SELECT id, is_active FROM Services WHERE id = ?', (service_id,))
        service = check_cursor.fetchone()
        if not service:
            current_app.logger.warning(f"Activate service {service_id}: Service not found.")
            return jsonify({"error": "Service not found"}), 404
        if service['is_active'] == 1:
            return jsonify({"message": "Service is already active.", "service": dict(service)}), 200
            
        db.execute('UPDATE Services SET is_active = 1 WHERE id = ?', (service_id,))
        db.commit()
        updated_service_cursor = db.execute('SELECT * FROM Services WHERE id = ?', (service_id,))
        updated_service = dict(updated_service_cursor.fetchone())
        current_app.logger.info(f"Service {service_id} activated successfully.")
        return jsonify({"message": "Service activated successfully", "service": updated_service}), 200
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error activating service {service_id}: {e}")
        return jsonify({"error": "Failed to activate service", "details": str(e)}), 500

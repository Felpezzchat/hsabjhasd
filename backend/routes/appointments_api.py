# backend/routes/appointments_api.py
import sqlite3
from flask import Blueprint, request, jsonify, current_app
from backend.database import get_db
import datetime # For parsing and validating datetime

appointments_bp = Blueprint('appointments_bp', __name__, url_prefix='/api/appointments')

def validate_iso_datetime(dt_str):
    """Validates if a string is in ISO 8601 datetime format (YYYY-MM-DDTHH:MM:SS)."""
    try:
        datetime.datetime.fromisoformat(dt_str)
        return True
    except ValueError:
        # Try to parse just date part if time is missing, common for date filters
        try:
            datetime.datetime.fromisoformat(dt_str + "T00:00:00")
            return True # Valid as a date, can be used for date comparisons
        except ValueError:
            return False


@appointments_bp.route('', methods=['GET'])
def get_appointments():
    current_app.logger.info(f"GET /api/appointments called with args: {request.args}")
    db = get_db()
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        customer_id = request.args.get('customer_id', type=int)
        service_id = request.args.get('service_id', type=int)
        status = request.args.get('status')

        query = '''
            SELECT 
                a.id, a.appointment_datetime, a.status, a.notes, a.price_at_booking,
                a.created_at, a.updated_at,
                c.id as customer_id, c.name as customer_name,
                s.id as service_id, s.name as service_name, s.duration_minutes as service_duration
            FROM Appointments a
            LEFT JOIN Customers c ON a.customer_id = c.id
            LEFT JOIN Services s ON a.service_id = s.id
        '''
        filters = []
        params = []

        if start_date_str:
            # Validate only the date part for range filtering
            if not validate_iso_datetime(start_date_str.split('T')[0]):
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
            filters.append("date(a.appointment_datetime) >= date(?)")
            params.append(start_date_str.split('T')[0])
        
        if end_date_str:
            if not validate_iso_datetime(end_date_str.split('T')[0]):
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400
            filters.append("date(a.appointment_datetime) <= date(?)")
            params.append(end_date_str.split('T')[0])

        if customer_id:
            filters.append("a.customer_id = ?")
            params.append(customer_id)
        
        if service_id:
            filters.append("a.service_id = ?")
            params.append(service_id)

        if status:
            filters.append("a.status = ?")
            params.append(status)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)
        
        query += " ORDER BY a.appointment_datetime DESC"

        current_app.logger.debug(f"Executing query: {query} with params: {params}")
        cursor = db.execute(query, tuple(params))
        appointments_rows = cursor.fetchall()
        appointments_list = [dict(row) for row in appointments_rows]
        return jsonify(appointments_list), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching appointments: {e}")
        return jsonify({"error": "Failed to fetch appointments", "details": str(e)}), 500

@appointments_bp.route('', methods=['POST'])
def add_appointment():
    current_app.logger.info(f"POST /api/appointments called with data: {request.json}")
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400
    
    data = request.json
    customer_id = data.get('customer_id', type=int) # Ensure type if possible
    service_id = data.get('service_id', type=int)
    appointment_datetime_str = data.get('appointment_datetime')
    status = data.get('status', 'Scheduled').strip() # Default status
    notes = data.get('notes', '').strip() or None

    if not customer_id:
        return jsonify({"error": "Customer ID is required and must be an integer."}), 400
    if not service_id:
        return jsonify({"error": "Service ID is required and must be an integer."}), 400
    if not appointment_datetime_str:
        return jsonify({"error": "Appointment datetime is required."}), 400
    
    if not validate_iso_datetime(appointment_datetime_str):
        return jsonify({"error": "Invalid appointment_datetime format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."}), 400

    db = get_db()
    try:
        # Validate customer_id exists
        customer_cursor = db.execute('SELECT id FROM Customers WHERE id = ?', (customer_id,))
        if not customer_cursor.fetchone():
            current_app.logger.warning(f"Add appointment: Customer with ID {customer_id} not found.")
            return jsonify({"error": f"Customer with ID {customer_id} not found."}), 404

        # Validate service_id exists and get its price
        service_cursor = db.execute('SELECT price, duration_minutes FROM Services WHERE id = ? AND is_active = 1', (service_id,))
        service_data = service_cursor.fetchone()
        if not service_data:
            current_app.logger.warning(f"Add appointment: Active service with ID {service_id} not found.")
            return jsonify({"error": f"Active service with ID {service_id} not found."}), 404
        
        price_at_booking = service_data['price']
        # service_duration = service_data['duration_minutes'] # For future use (e.g., overlap checks)

        cursor = db.execute(
            'INSERT INTO Appointments (customer_id, service_id, appointment_datetime, status, notes, price_at_booking, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)',
            (customer_id, service_id, appointment_datetime_str, status, notes, price_at_booking)
        )
        db.commit()
        new_appointment_id = cursor.lastrowid
        
        stmt = '''
            SELECT 
                a.id, a.appointment_datetime, a.status, a.notes, a.price_at_booking,
                a.created_at, a.updated_at,
                c.id as customer_id, c.name as customer_name,
                s.id as service_id, s.name as service_name, s.duration_minutes as service_duration
            FROM Appointments a
            LEFT JOIN Customers c ON a.customer_id = c.id
            LEFT JOIN Services s ON a.service_id = s.id
            WHERE a.id = ?
        '''
        appointment_cursor = db.execute(stmt, (new_appointment_id,))
        created_appointment = dict(appointment_cursor.fetchone())
        current_app.logger.info(f"Appointment ID {new_appointment_id} created successfully.")
        return jsonify(created_appointment), 201
    except sqlite3.IntegrityError as e:
        db.rollback()
        current_app.logger.error(f"Integrity error adding appointment: {e}")
        return jsonify({"error": "Database integrity error. Ensure customer and service exist.", "details": str(e)}), 409
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Unexpected error adding appointment: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    current_app.logger.info(f"GET /api/appointments/{appointment_id} called")
    db = get_db()
    try:
        stmt = '''
            SELECT 
                a.id, a.appointment_datetime, a.status, a.notes, a.price_at_booking,
                a.created_at, a.updated_at,
                c.id as customer_id, c.name as customer_name, c.email as customer_email, c.phone as customer_phone,
                s.id as service_id, s.name as service_name, s.duration_minutes as service_duration, s.price as service_current_price
            FROM Appointments a
            LEFT JOIN Customers c ON a.customer_id = c.id
            LEFT JOIN Services s ON a.service_id = s.id
            WHERE a.id = ?
        '''
        cursor = db.execute(stmt, (appointment_id,))
        appointment = cursor.fetchone()
        if appointment:
            return jsonify(dict(appointment)), 200
        current_app.logger.warning(f"GET /api/appointments/{appointment_id}: Appointment not found.")
        return jsonify({"error": "Appointment not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching appointment {appointment_id}: {e}")
        return jsonify({"error": "Failed to fetch appointment details", "details": str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    current_app.logger.info(f"PUT /api/appointments/{appointment_id} called with data: {request.json}")
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.json
    db = get_db()

    try:
        current_appointment_cursor = db.execute('SELECT * FROM Appointments WHERE id = ?', (appointment_id,))
        current_appointment = current_appointment_cursor.fetchone()
        if not current_appointment:
            current_app.logger.warning(f"Update appointment {appointment_id}: Appointment not found.")
            return jsonify({"error": "Appointment not found"}), 404

        customer_id = data.get('customer_id', current_appointment['customer_id'])
        service_id = data.get('service_id', current_appointment['service_id'])
        appointment_datetime_str = data.get('appointment_datetime', current_appointment['appointment_datetime'])
        status = data.get('status', current_appointment['status']).strip()
        notes = data.get('notes', current_appointment['notes'] if current_appointment['notes'] is not None else '').strip() or None


        if not customer_id: return jsonify({"error": "Customer ID is required."}), 400
        if not service_id: return jsonify({"error": "Service ID is required."}), 400
        if not appointment_datetime_str: return jsonify({"error": "Appointment datetime is required."}), 400
        if not validate_iso_datetime(appointment_datetime_str):
            return jsonify({"error": "Invalid appointment_datetime format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."}), 400

        # Validate customer_id exists
        customer_cursor = db.execute('SELECT id FROM Customers WHERE id = ?', (customer_id,))
        if not customer_cursor.fetchone():
            current_app.logger.warning(f"Update appointment {appointment_id}: Customer with ID {customer_id} not found.")
            return jsonify({"error": f"Customer with ID {customer_id} not found."}), 404

        # Validate service_id exists and update price_at_booking if service changed
        price_at_booking = current_appointment['price_at_booking']
        if service_id != current_appointment['service_id']:
            service_cursor = db.execute('SELECT price FROM Services WHERE id = ? AND is_active = 1', (service_id,))
            service_data = service_cursor.fetchone()
            if not service_data:
                current_app.logger.warning(f"Update appointment {appointment_id}: Active service with ID {service_id} not found.")
                return jsonify({"error": f"Active service with ID {service_id} not found."}), 404
            price_at_booking = service_data['price']
        
        db.execute(
            'UPDATE Appointments SET customer_id = ?, service_id = ?, appointment_datetime = ?, status = ?, notes = ?, price_at_booking = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (customer_id, service_id, appointment_datetime_str, status, notes, price_at_booking, appointment_id)
        )
        db.commit()
        
        stmt = '''
            SELECT 
                a.id, a.appointment_datetime, a.status, a.notes, a.price_at_booking,
                a.created_at, a.updated_at,
                c.id as customer_id, c.name as customer_name,
                s.id as service_id, s.name as service_name, s.duration_minutes as service_duration
            FROM Appointments a
            LEFT JOIN Customers c ON a.customer_id = c.id
            LEFT JOIN Services s ON a.service_id = s.id
            WHERE a.id = ?
        '''
        updated_appointment_cursor = db.execute(stmt, (appointment_id,))
        updated_appointment = dict(updated_appointment_cursor.fetchone())
        current_app.logger.info(f"Appointment ID {appointment_id} updated successfully.")
        return jsonify(updated_appointment), 200
    except sqlite3.IntegrityError as e:
        db.rollback()
        current_app.logger.error(f"Integrity error updating appointment {appointment_id}: {e}")
        return jsonify({"error": "Database integrity error. Ensure customer and service exist.", "details": str(e)}), 409
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Unexpected error updating appointment {appointment_id}: {e}")
        return jsonify({"error": "An unexpected error occurred during update", "details": str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    current_app.logger.info(f"DELETE /api/appointments/{appointment_id} called")
    db = get_db()
    try:
        check_cursor = db.execute('SELECT id FROM Appointments WHERE id = ?', (appointment_id,))
        if not check_cursor.fetchone():
            current_app.logger.warning(f"Delete appointment {appointment_id}: Appointment not found.")
            return jsonify({"error": "Appointment not found"}), 404
                
        db.execute('DELETE FROM Appointments WHERE id = ?', (appointment_id,))
        db.commit()
        current_app.logger.info(f"Appointment ID {appointment_id} deleted successfully.")
        return jsonify({"message": "Appointment deleted successfully"}), 200
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error deleting appointment {appointment_id}: {e}")
        return jsonify({"error": "Failed to delete appointment", "details": str(e)}), 500

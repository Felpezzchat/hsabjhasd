# backend/routes/products_api.py
import sqlite3
from flask import Blueprint, request, jsonify, current_app
from backend.database import get_db
import datetime # For parsing and validating date

products_bp = Blueprint('products_bp', __name__, url_prefix='/api/products')

def validate_iso_date(date_str):
    """Validates if a string is in YYYY-MM-DD format or YYYY-MM-DDTHH:MM:SS. Returns YYYY-MM-DD or None."""
    if not date_str: return None # Allow NULL dates explicitly
    try:
        # Handles both YYYY-MM-DD and YYYY-MM-DDTHH:MM:SS by taking the date part
        return datetime.date.fromisoformat(date_str.split('T')[0]).isoformat()
    except ValueError:
        return None

@products_bp.route('', methods=['GET'])
def get_products():
    current_app.logger.info(f"GET /api/products called with args: {request.args}")
    db = get_db()
    try:
        low_stock = request.args.get('low_stock', 'false').lower() == 'true'
        nearing_expiry_days_str = request.args.get('nearing_expiry_days')

        query = 'SELECT * FROM Products'
        filters = []
        params = []

        if low_stock:
            filters.append("(quantity_on_hand <= reorder_level AND reorder_level > 0)")
        
        if nearing_expiry_days_str is not None:
            try:
                nearing_expiry_days = int(nearing_expiry_days_str)
                if nearing_expiry_days > 0:
                    target_date = (datetime.date.today() + datetime.timedelta(days=nearing_expiry_days)).isoformat()
                    today_str = datetime.date.today().isoformat()
                    filters.append("expiry_date IS NOT NULL AND date(expiry_date) <= date(?) AND date(expiry_date) >= date(?)")
                    params.extend([target_date, today_str])
                elif nearing_expiry_days == 0: # expired today or before
                    today_str = datetime.date.today().isoformat()
                    filters.append("expiry_date IS NOT NULL AND date(expiry_date) <= date(?)")
                    params.append(today_str)

            except ValueError:
                current_app.logger.warning("Invalid value for nearing_expiry_days, must be an integer.")
                # Optionally return a 400 error here, or just ignore the filter
        
        if filters:
            query += " WHERE " + " AND ".join(filters)
        
        query += ' ORDER BY name'
        
        current_app.logger.debug(f"Executing query: {query} with params: {params}")
        cursor = db.execute(query, tuple(params))
        products_rows = cursor.fetchall()
        products_list = [dict(row) for row in products_rows]
        return jsonify(products_list), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching products: {e}")
        return jsonify({"error": "Failed to fetch products", "details": str(e)}), 500

@products_bp.route('', methods=['POST'])
def add_product():
    current_app.logger.info(f"POST /api/products called with data: {request.json}")
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400
    
    data = request.json
    name = data.get('name', '').strip()
    brand = data.get('brand', '').strip() or None
    description = data.get('description', '').strip() or None
    sku = data.get('sku', '').strip() or None
    supplier = data.get('supplier', '').strip() or None
    purchase_price_str = data.get('purchase_price')
    sale_price_str = data.get('sale_price')
    quantity_on_hand_str = data.get('quantity_on_hand', '0') # Default to '0' as string for consistent parsing
    reorder_level_str = data.get('reorder_level', '0')
    expiry_date_input = data.get('expiry_date', '').strip() or None

    if not name: return jsonify({"error": "Product name is required."}), 400
    if sale_price_str is None: return jsonify({"error": "Sale price is required."}), 400
    if quantity_on_hand_str is None: return jsonify({"error": "Quantity on hand is required (can be 0)."}), 400

    purchase_price, sale_price, quantity_on_hand, reorder_level = None, None, 0, 0
    try:
        if purchase_price_str is not None: purchase_price = float(purchase_price_str)
        sale_price = float(sale_price_str) # Required
        quantity_on_hand = int(quantity_on_hand_str) # Required
        if reorder_level_str is not None: reorder_level = int(reorder_level_str)

        if purchase_price is not None and purchase_price < 0: return jsonify({"error": "Purchase price cannot be negative."}), 400
        if sale_price < 0: return jsonify({"error": "Sale price cannot be negative."}), 400
        if quantity_on_hand < 0: return jsonify({"error": "Quantity on hand cannot be negative."}), 400
        if reorder_level < 0: return jsonify({"error": "Reorder level cannot be negative."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid number format for price, quantity, or reorder level."}), 400

    expiry_date_iso = validate_iso_date(expiry_date_input)
    if expiry_date_input and not expiry_date_iso: # If input was given but validation failed
        return jsonify({"error": "Invalid expiry_date format. Use YYYY-MM-DD."}), 400
        
    db = get_db()
    try:
        cursor = db.execute(
            '''INSERT INTO Products 
               (name, brand, description, sku, supplier, purchase_price, sale_price, quantity_on_hand, reorder_level, expiry_date, last_stocked_date, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)''',
            (name, brand, description, sku, supplier, purchase_price, sale_price, quantity_on_hand, reorder_level, expiry_date_iso)
        )
        db.commit()
        new_product_id = cursor.lastrowid
        product_cursor = db.execute('SELECT * FROM Products WHERE id = ?', (new_product_id,))
        created_product = dict(product_cursor.fetchone())
        current_app.logger.info(f"Product '{name}' (ID: {new_product_id}) added successfully.")
        return jsonify(created_product), 201
    except sqlite3.IntegrityError as e:
        db.rollback()
        err_detail = str(e).lower()
        if sku and 'products.sku' in err_detail:
             return jsonify({"error": f"Product with SKU '{sku}' already exists."}), 409
        if 'products.name' in err_detail:
             return jsonify({"error": f"Product with name '{name}' already exists."}), 409
        current_app.logger.error(f"Integrity error adding product: {e}")
        return jsonify({"error": "Database integrity error. SKU or Name may already exist.", "details": str(e)}), 409
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Unexpected error adding product: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    current_app.logger.info(f"GET /api/products/{product_id} called")
    db = get_db()
    try:
        cursor = db.execute('SELECT * FROM Products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        if product:
            return jsonify(dict(product)), 200
        current_app.logger.warning(f"GET /api/products/{product_id}: Product not found.")
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching product {product_id}: {e}")
        return jsonify({"error": "Failed to fetch product details", "details": str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    current_app.logger.info(f"PUT /api/products/{product_id} called with data: {request.json}")
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.json
    db = get_db()

    try:
        current_product_cursor = db.execute('SELECT * FROM Products WHERE id = ?', (product_id,))
        current_product = current_product_cursor.fetchone()
        if not current_product:
            current_app.logger.warning(f"Update product {product_id}: Product not found.")
            return jsonify({"error": "Product not found"}), 404

        name = data.get('name', current_product['name']).strip()
        if not name: return jsonify({"error": "Product name cannot be empty."}), 400

        brand = data.get('brand', current_product['brand'])
        description = data.get('description', current_product['description'])
        sku = data.get('sku', current_product['sku'])
        supplier = data.get('supplier', current_product['supplier'])
        
        # Handle numeric types carefully, allowing for updates
        purchase_price = data.get('purchase_price', current_product['purchase_price'])
        sale_price = data.get('sale_price', current_product['sale_price'])
        quantity_on_hand = data.get('quantity_on_hand', current_product['quantity_on_hand'])
        reorder_level = data.get('reorder_level', current_product['reorder_level'])
        expiry_date_input = data.get('expiry_date', current_product['expiry_date'])
        
        last_stocked_date = current_product['last_stocked_date']
        if 'quantity_on_hand' in data and data.get('quantity_on_hand') is not None:
            try:
                new_qty = int(data['quantity_on_hand'])
                if new_qty > current_product['quantity_on_hand']:
                    last_stocked_date = datetime.datetime.now().isoformat(timespec='seconds')
                quantity_on_hand = new_qty # Ensure it's an int
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid quantity_on_hand format."}), 400
        
        if 'last_stocked_date' in data: # Allow explicit update
            lsd_input = data['last_stocked_date']
            validated_lsd = validate_iso_date(lsd_input.split('T')[0] + "T00:00:00") if lsd_input else None # Allow clearing
            if lsd_input and not validated_lsd:
                return jsonify({"error": "Invalid last_stocked_date format. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS."}), 400
            last_stocked_date = lsd_input # Store as provided if valid, or None

        try:
            if purchase_price is not None: purchase_price = float(purchase_price)
            if sale_price is not None: sale_price = float(sale_price) # Should always have a value
            else: return jsonify({"error": "Sale price is required."}), 400 # Cannot be None
            
            if quantity_on_hand is not None: quantity_on_hand = int(quantity_on_hand)
            else: return jsonify({"error": "Quantity on hand is required."}), 400 # Cannot be None

            if reorder_level is not None: reorder_level = int(reorder_level)
            else: reorder_level = 0 # Default if None

            if purchase_price is not None and purchase_price < 0: return jsonify({"error": "Purchase price cannot be negative."}), 400
            if sale_price < 0: return jsonify({"error": "Sale price cannot be negative."}), 400
            if quantity_on_hand < 0: return jsonify({"error": "Quantity cannot be negative."}), 400
            if reorder_level < 0: return jsonify({"error": "Reorder level cannot be negative."}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid number format for price, quantity, or reorder level."}), 400

        expiry_date_iso = validate_iso_date(expiry_date_input)
        if expiry_date_input and not expiry_date_iso:
            return jsonify({"error": "Invalid expiry_date format. Use YYYY-MM-DD."}), 400

        db.execute(
            '''UPDATE Products SET 
               name = ?, brand = ?, description = ?, sku = ?, supplier = ?, 
               purchase_price = ?, sale_price = ?, quantity_on_hand = ?, reorder_level = ?, 
               expiry_date = ?, last_stocked_date = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (name, brand, description, sku, supplier, purchase_price, sale_price, quantity_on_hand, reorder_level, expiry_date_iso, last_stocked_date, product_id)
        )
        db.commit()
        updated_product_cursor = db.execute('SELECT * FROM Products WHERE id = ?', (product_id,))
        updated_product = dict(updated_product_cursor.fetchone())
        current_app.logger.info(f"Product ID {product_id} updated successfully.")
        return jsonify(updated_product), 200
    except sqlite3.IntegrityError as e:
        db.rollback()
        err_detail = str(e).lower()
        if sku and 'products.sku' in err_detail:
             return jsonify({"error": f"Product with SKU '{sku}' already exists for another product."}), 409
        if 'products.name' in err_detail: # Name is unique
             return jsonify({"error": f"Product with name '{name}' already exists for another product."}), 409
        current_app.logger.error(f"Integrity error updating product {product_id}: {e}")
        return jsonify({"error": "Database integrity error. SKU or Name may already exist.", "details": str(e)}), 409
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Unexpected error updating product {product_id}: {e}")
        return jsonify({"error": "An unexpected error occurred during update", "details": str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    current_app.logger.info(f"DELETE /api/products/{product_id} called")
    db = get_db()
    try:
        check_cursor = db.execute('SELECT id FROM Products WHERE id = ?', (product_id,))
        if not check_cursor.fetchone():
            current_app.logger.warning(f"Delete product {product_id}: Product not found.")
            return jsonify({"error": "Product not found"}), 404
                
        # ProductUsage has ON DELETE CASCADE for product_id
        db.execute('DELETE FROM Products WHERE id = ?', (product_id,))
        db.commit()
        current_app.logger.info(f"Product ID {product_id} deleted successfully.")
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error deleting product {product_id}: {e}")
        return jsonify({"error": "Failed to delete product", "details": str(e)}), 500

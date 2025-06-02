from flask import Flask, jsonify 
from config import Config
import backend.database as database 
from backend.routes.customers_api import customers_bp 
from backend.routes.services_api import services_bp 
from backend.routes.appointments_api import appointments_bp 
from backend.routes.products_api import products_bp
from backend.routes.photo_server_api import photos_bp as photo_server_blueprint # Import photo server blueprint
import logging

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
log_level = logging.DEBUG if app.debug else logging.INFO
logging.basicConfig(level=log_level, 
                    format='[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s L%(lineno)d: %(message)s')
app.logger.setLevel(log_level)


# Initialize database handling
database.init_app(app)

# Register Blueprints
app.logger.info("Registering blueprints...")
app.register_blueprint(customers_bp) 
app.logger.info(f"Registered blueprint: '{customers_bp.name}' with URL prefix '{customers_bp.url_prefix}'")
app.register_blueprint(services_bp) 
app.logger.info(f"Registered blueprint: '{services_bp.name}' with URL prefix '{services_bp.url_prefix}'")
app.register_blueprint(appointments_bp) 
app.logger.info(f"Registered blueprint: '{appointments_bp.name}' with URL prefix '{appointments_bp.url_prefix}'")
app.register_blueprint(products_bp)
app.logger.info(f"Registered blueprint: '{products_bp.name}' with URL prefix '{products_bp.url_prefix}'")
app.register_blueprint(photo_server_blueprint) # Register photo server
app.logger.info(f"Registered blueprint: '{photo_server_blueprint.name}' with URL prefix '{photo_server_blueprint.url_prefix}'")


@app.route('/')
def home():
    app.logger.info("Home route '/' accessed.")
    return "Salon Management Backend is Running!"

@app.route('/api/external/some-service', methods=['GET'])
def call_external_service():
    app.logger.info("GET /api/external/some-service accessed.")
    return jsonify({"message": "Conceptual external API call (placeholder)", "data": {"info": "some data from external service"}})

if __name__ == '__main__':
    app.logger.info(f"Starting Flask development server directly via __main__ on port 5001. Debug mode is {'on' if app.debug else 'off'}.")
    app.run(host='0.0.0.0', port=5001)

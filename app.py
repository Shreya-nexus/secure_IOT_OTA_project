import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import init_db, close_db
from routes.device_routes import device_bp
from routes.firmware_routes import firmware_bp
from routes.update_routes import update_bp

def setup_logging():
    """Configure file and console logging."""
    os.makedirs(Config.LOG_DIR, exist_ok=True)

    logger = logging.getLogger("ota_system")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if logger.handlers:
        return logger

    # File Handler
    file_handler = logging.FileHandler(Config.LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    file_handler.setFormatter(file_formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def create_app(config_class=Config):
    """Application factory for Flask backend."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for future frontend integration
    CORS(app)

    # Initialize Logging
    logger = setup_logging()
    logger.info("Initializing Secure IoT OTA Backend Server...")

    # Database Initialization & Context Teardown
    with app.app_context():
        init_db()

    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(device_bp)
    app.register_blueprint(firmware_bp)
    app.register_blueprint(update_bp)

    # Global Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": getattr(error, "description", "Bad Request")}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": getattr(error, "description", "Unauthorized")}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": getattr(error, "description", "Forbidden")}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": getattr(error, "description", "Resource Not Found")}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method Not Allowed"}), 405

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({"error": getattr(error, "description", "Conflict")}), 409

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"error": "Payload exceeds maximum allowed size (16MB)"}), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error("Internal Server Error: %s", str(error))
        return jsonify({"error": "Internal Server Error"}), 500

    # Root route for server health check
    @app.route("/", methods=["GET"])
    def root_status():
        return jsonify({
            "system": "Secure IoT OTA Firmware Update Server",
            "status": "online",
            "version": "1.0.0"
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

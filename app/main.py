from flask import Flask, jsonify
from app.auth.routes import bp as auth_bp
from app.subscriptions.routes import bp as subscriptions_bp
from app.config import Config
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler
import signal
import sys


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints with /subs prefix
    app.register_blueprint(auth_bp, url_prefix='/subs/auth')
    app.register_blueprint(subscriptions_bp, url_prefix='/subs/subscriptions')

    # Set debug mode based on environment
    app.debug = os.getenv('FLASK_ENV') == 'development'

    # Enable CORS
    CORS(app)

    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

    def handle_sigterm(*args):
        app.logger.info('Received SIGTERM, shutting down...')
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_sigterm)

    @app.route('/subs/health')
    def health_check():
        return jsonify({"status": "UP"}), 200

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error"}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.debug, port=8000)

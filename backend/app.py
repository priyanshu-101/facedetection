from flask import Flask, jsonify
from flask_cors import CORS
from models.database import db_instance
from dotenv import load_dotenv
import os
import json
import numpy as np

# Custom JSON encoder to handle numpy arrays
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super(NumpyEncoder, self).default(obj)

# Load environment variables
load_dotenv()

def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # Set custom JSON encoder to handle numpy arrays
    app.json_encoder = NumpyEncoder
    
    # Enable CORS for all routes
    CORS(app, origins=["*"])
    
    # Import flexible routes only
    try:
        from routes.api_routes_flexible import api
        print("Using flexible API routes with automatic face recognition method detection")
    except ImportError:
        print("ERROR: Could not import flexible API routes")
        return None
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({'error': 'File too large (max 16MB)'}), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Face Detection API',
            'version': '1.0.0',
            'endpoints': {
                'register': '/api/register (POST)',
                'detect': '/api/detect (POST)',
                'users': '/api/users (GET)',
                'user': '/api/user/<user_id> (GET, DELETE)',
                'health': '/api/health (GET)',
                'info': '/api/info (GET)'
            }
        })
    
    return app

def main():
    """Main function to run the application"""
    try:
        # Test database connection
        db = db_instance.get_database()
        print("Database connection successful")
        
        # Create Flask app
        app = create_app()
        
        # Get port from environment or use default
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_ENV') == 'development'
        
        print(f"Starting Face Detection API on port {port}")
        print(f"Debug mode: {debug}")
        print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
        
        # Run the application
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
        
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1
    
    finally:
        # Close database connection on shutdown
        try:
            db_instance.close_connection()
        except:
            pass

if __name__ == '__main__':
    exit(main())

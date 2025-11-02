from flask import Flask
from flask_cors import CORS
from models import db
from auth import auth_bp
from routes import api_bp
import os
from datetime import timedelta


def create_app():
    """
    Application factory function to create and configure the Flask app.
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Session configuration - Make sessions persistent across browser refreshes
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True  # Make sessions permanent (survive browser refresh)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Sessions last 7 days
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_NAME'] = 'todo_session'
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow cookies from localhost:5000 to work with localhost:3000
    app.config['SESSION_COOKIE_PATH'] = '/'
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure CORS to allow credentials (cookies/sessions)
    CORS(app,
         resources={r"/api/*": {
             "origins": ["http://localhost:3000"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type"],
             "supports_credentials": True
         }})
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)  # PR-4: List management routes
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    # Health check endpoint
    @app.route('/')
    def index():
        return {'message': 'Hierarchical Todo List API', 'status': 'running'}, 200
    
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app


if __name__ == '__main__':
    app = create_app()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
from flask import Flask
from flask_cors import CORS
from models import db
from auth import auth_bp
import os


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
    
    # Session configuration
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure CORS to allow credentials (cookies/sessions)
    CORS(app, 
         origins=['http://localhost:3000'],
         supports_credentials=True,
         allow_headers=['Content-Type'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    # app.register_blueprint(api_bp)  # Will be added in PR-4
    
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
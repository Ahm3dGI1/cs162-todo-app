from flask import Blueprint, request, jsonify, session
from models import db, User
from functools import wraps

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def login_required(f):
    """
    Decorator to protect routes that require authentication.
    
    Usage:
        @auth_bp.route('/protected')
        @login_required
        def protected_route():
            # Only accessible to logged-in users
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    
    Expected JSON body:
        {
            "username": "string",
            "email": "string",
            "password": "string"
        }
    
    Returns:
        201: User created successfully
        400: Validation error or user already exists
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    
    # Validate input lengths
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters long'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    try:
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in immediately after registration
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and create a session.
    
    Expected JSON body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        200: Login successful
        401: Invalid credentials
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    username = data['username'].strip()
    password = data['password']
    
    # Find user by username
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Create session
    session['user_id'] = user.id
    session['username'] = user.username
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Log out the current user by clearing the session.
    
    Returns:
        200: Logout successful
    """
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/current', methods=['GET'])
def get_current_user():
    """
    Get the currently logged-in user's information.
    
    Returns:
        200: User data if logged in
        401: Not authenticated
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    
    if not user:
        # User was deleted but session still exists
        session.clear()
        return jsonify({'error': 'User not found'}), 401
    
    return jsonify({'user': user.to_dict()}), 200
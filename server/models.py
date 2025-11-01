from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Primary key
        username: Unique username for login
        email: Unique email address
        password_hash: Hashed password for security
        lists: Relationship to user's todo lists
        todos: Relationship to user's todo items
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lists = db.relationship('TodoList', backref='owner', lazy=True, cascade='all, delete-orphan')
    todos = db.relationship('TodoItem', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class TodoList(db.Model):
    """
    TodoList model for organizing todos into separate lists.

    Attributes:
        id: Primary key
        name: Name of the todo list
        user_id: Foreign key to the owner user
        todos: Relationship to todo items in this list
        created_at: Timestamp of creation
    """
    __tablename__ = 'todo_lists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    todos = db.relationship('TodoItem', backref='list', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Convert list to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }


class TodoItem(db.Model):
    """
    TodoItem model for individual todo tasks with hierarchical support.

    Attributes:
        id: Primary key
        title: Title of the todo item
        description: Optional detailed description
        completed: Whether the task is completed
        collapsed: Whether subtasks are collapsed in UI
        depth: Hierarchical depth (0=top-level, 1=subtask, 2=sub-subtask)
        parent_id: Foreign key to parent todo (null for top-level)
        list_id: Foreign key to the containing list
        user_id: Foreign key to the owner user
        children: Relationship to child todos
        created_at: Timestamp of creation
    """
    __tablename__ = 'todo_items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    collapsed = db.Column(db.Boolean, default=False, nullable=False)
    depth = db.Column(db.Integer, default=0, nullable=False)
    priority = db.Column(db.String(10), default='medium', nullable=False)

    # Foreign keys
    parent_id = db.Column(db.Integer, db.ForeignKey('todo_items.id'), index=True)
    list_id = db.Column(db.Integer, db.ForeignKey('todo_lists.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Self-referential relationship for hierarchy
    children = db.relationship('TodoItem',
                               backref=db.backref('parent', remote_side=[id]),
                               lazy=True,
                               cascade='all, delete-orphan')

    def to_dict(self, include_children=False):
        """
        Convert todo item to dictionary.

        Args:
            include_children: Whether to recursively include child todos
        """
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'collapsed': self.collapsed,
            'depth': self.depth,
            'priority': self.priority,
            'parent_id': self.parent_id,
            'list_id': self.list_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }

        if include_children:
            result['children'] = [child.to_dict(include_children=True) for child in self.children]

        return result
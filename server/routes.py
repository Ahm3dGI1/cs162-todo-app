from flask import Blueprint, request, jsonify, session
from models import db, TodoList, TodoItem, User
from auth import login_required

# Create API blueprint for list and todo routes
api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============================================================================
# PROJECT ROUTES (PR-4)
# ============================================================================

@api_bp.route('/projects', methods=['GET'])
@login_required
def get_projects():
    """
    Get all projects for the current user.

    Returns:
        200: List of user's projects
        401: Not authenticated
    """
    user_id = session.get('user_id')

    # Get all projects owned by this user
    projects = TodoList.query.filter_by(user_id=user_id).order_by(TodoList.created_at).all()

    return jsonify({
        'projects': [project.to_dict() for project in projects]
    }), 200


@api_bp.route('/projects', methods=['POST'])
@login_required
def create_project():
    """
    Create a new project.

    Expected JSON body:
        {
            "name": "string"
        }

    Returns:
        201: Project created successfully
        400: Validation error
        401: Not authenticated
    """
    user_id = session.get('user_id')
    data = request.get_json()

    # Validate required fields
    if not data or not data.get('name'):
        return jsonify({'error': 'Project name is required'}), 400

    name = data['name'].strip()

    # Validate name length
    if len(name) < 1:
        return jsonify({'error': 'Project name cannot be empty'}), 400

    if len(name) > 200:
        return jsonify({'error': 'Project name must be 200 characters or less'}), 400

    # Create new project
    try:
        new_project = TodoList(
            name=name,
            user_id=user_id
        )

        db.session.add(new_project)
        db.session.commit()

        return jsonify({
            'message': 'Project created successfully',
            'project': new_project.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create project: {str(e)}'}), 500


@api_bp.route('/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """
    Update a project's name.

    Expected JSON body:
        {
            "name": "string"
        }

    Args:
        project_id: ID of the project to update

    Returns:
        200: Project updated successfully
        400: Validation error
        401: Not authenticated
        403: Not authorized to update this project
        404: Project not found
    """
    user_id = session.get('user_id')
    data = request.get_json()

    # Validate required fields
    if not data or not data.get('name'):
        return jsonify({'error': 'Project name is required'}), 400

    name = data['name'].strip()

    # Validate name length
    if len(name) < 1:
        return jsonify({'error': 'Project name cannot be empty'}), 400

    if len(name) > 200:
        return jsonify({'error': 'Project name must be 200 characters or less'}), 400

    # Find the project
    project = TodoList.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    # Check ownership
    if project.user_id != user_id:
        return jsonify({'error': 'Not authorized to update this project'}), 403

    # Update the project
    try:
        project.name = name
        db.session.commit()

        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update project: {str(e)}'}), 500


@api_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """
    Delete a project and all its todos.

    Args:
        project_id: ID of the project to delete

    Returns:
        200: Project deleted successfully
        401: Not authenticated
        403: Not authorized to delete this project
        404: Project not found
    """
    user_id = session.get('user_id')

    # Find the project
    project = TodoList.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    # Check ownership
    if project.user_id != user_id:
        return jsonify({'error': 'Not authorized to delete this project'}), 403

    # Delete the project (cascade will delete all todos)
    try:
        db.session.delete(project)
        db.session.commit()

        return jsonify({
            'message': 'Project deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete project: {str(e)}'}), 500


# ============================================================================
# TODO ROUTES (PR-6 - Top-Level Only)
# ============================================================================

@api_bp.route('/todos/<int:project_id>', methods=['GET'])
@login_required
def get_todos(project_id):
    """
    Get all todos for a specific project (Returns hierarchical structure).

    Args:
        project_id: ID of the project to get todos from

    Returns:
        200: Hierarchical list of todos (only top-level, with nested children)
        401: Not authenticated
        403: Not authorized to access this project
        404: Project not found
    """
    user_id = session.get('user_id')

    # Find the project
    project = TodoList.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    # Check ownership
    if project.user_id != user_id:
        return jsonify({'error': 'Not authorized to access this project'}), 403

    # Get all top-level todos (parent_id is null) with their children
    todos = TodoItem.query.filter_by(
        list_id=project_id,
        parent_id=None
    ).order_by(TodoItem.created_at).all()

    # Return hierarchical structure with children
    return jsonify({
        'todos': [todo.to_dict(include_children=True) for todo in todos]
    }), 200


@api_bp.route('/todos', methods=['POST'])
@login_required
def create_todo():
    """
    Create a new todo item (Now supports parent_id for hierarchical todos).

    Expected JSON body:
        {
            "project_id": integer,
            "title": "string",
            "description": "string" (optional),
            "parent_id": integer (optional, for subtasks)
        }

    Returns:
        201: Todo created successfully
        400: Validation error (including depth limit)
        401: Not authenticated
        403: Not authorized to add to this project
        404: Project or parent todo not found
    """
    user_id = session.get('user_id')
    data = request.get_json()

    # Validate required fields
    if not data or not data.get('project_id') or not data.get('title'):
        return jsonify({'error': 'project_id and title are required'}), 400

    project_id = data['project_id']
    title = data['title'].strip()
    description = data.get('description', '').strip()
    parent_id = data.get('parent_id')  # Now accepting parent_id

    # Validate title length
    if len(title) < 1:
        return jsonify({'error': 'Title cannot be empty'}), 400

    if len(title) > 500:
        return jsonify({'error': 'Title must be 500 characters or less'}), 400

    # Find the project
    project = TodoList.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    # Check ownership
    if project.user_id != user_id:
        return jsonify({'error': 'Not authorized to add to this project'}), 403

    # Calculate depth based on parent
    depth = 0
    if parent_id:
        parent_todo = TodoItem.query.get(parent_id)

        if not parent_todo:
            return jsonify({'error': 'Parent todo not found'}), 404

        # Verify parent belongs to user and same project
        if parent_todo.user_id != user_id:
            return jsonify({'error': 'Not authorized to add subtask to this todo'}), 403

        if parent_todo.list_id != project_id:
            return jsonify({'error': 'Parent todo must be in the same project'}), 400

        # Calculate depth (max depth is 2, meaning levels 0, 1, 2)
        depth = parent_todo.depth + 1

        if depth > 2:
            return jsonify({'error': 'Maximum nesting depth reached (3 levels max)'}), 400

    # Create new todo
    try:
        new_todo = TodoItem(
            title=title,
            description=description,
            list_id=project_id,
            user_id=user_id,
            parent_id=parent_id,
            depth=depth,
            completed=False,
            collapsed=False
        )

        db.session.add(new_todo)
        db.session.commit()

        return jsonify({
            'message': 'Todo created successfully',
            'todo': new_todo.to_dict(include_children=True)  # Include children for hierarchical display
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create todo: {str(e)}'}), 500


@api_bp.route('/todos/<int:todo_id>', methods=['PUT'])
@login_required
def update_todo(todo_id):
    """
    Update a todo item.

    Expected JSON body:
        {
            "title": "string" (optional),
            "description": "string" (optional),
            "completed": boolean (optional)
        }

    Args:
        todo_id: ID of the todo to update

    Returns:
        200: Todo updated successfully
        400: Validation error
        401: Not authenticated
        403: Not authorized to update this todo
        404: Todo not found
    """
    user_id = session.get('user_id')
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Find the todo
    todo = TodoItem.query.get(todo_id)

    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    # Check ownership
    if todo.user_id != user_id:
        return jsonify({'error': 'Not authorized to update this todo'}), 403

    # Update fields if provided
    try:
        if 'title' in data:
            title = data['title'].strip()
            if len(title) < 1:
                return jsonify({'error': 'Title cannot be empty'}), 400
            if len(title) > 500:
                return jsonify({'error': 'Title must be 500 characters or less'}), 400
            todo.title = title

        if 'description' in data:
            todo.description = data['description'].strip()

        if 'completed' in data:
            todo.completed = bool(data['completed'])

        db.session.commit()

        return jsonify({
            'message': 'Todo updated successfully',
            'todo': todo.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update todo: {str(e)}'}), 500


@api_bp.route('/todos/<int:todo_id>', methods=['DELETE'])
@login_required
def delete_todo(todo_id):
    """
    Delete a todo item.

    Args:
        todo_id: ID of the todo to delete

    Returns:
        200: Todo deleted successfully
        401: Not authenticated
        403: Not authorized to delete this todo
        404: Todo not found
    """
    user_id = session.get('user_id')

    # Find the todo
    todo = TodoItem.query.get(todo_id)

    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    # Check ownership
    if todo.user_id != user_id:
        return jsonify({'error': 'Not authorized to delete this todo'}), 403

    # Delete the todo
    try:
        db.session.delete(todo)
        db.session.commit()

        return jsonify({
            'message': 'Todo deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete todo: {str(e)}'}), 500

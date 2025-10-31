from flask import Blueprint, request, jsonify, session
from models import db, TodoList, TodoItem, User
from auth import login_required

# Create API blueprint for list and todo routes
api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============================================================================
# LIST ROUTES (PR-4)
# ============================================================================

@api_bp.route('/lists', methods=['GET'])
@login_required
def get_lists():
    """
    Get all todo lists for the current user.

    Returns:
        200: List of user's todo lists
        401: Not authenticated
    """
    user_id = session.get('user_id')

    # Get all lists owned by this user
    lists = TodoList.query.filter_by(user_id=user_id).order_by(TodoList.created_at).all()

    return jsonify({
        'lists': [todo_list.to_dict() for todo_list in lists]
    }), 200


@api_bp.route('/lists', methods=['POST'])
@login_required
def create_list():
    """
    Create a new todo list.

    Expected JSON body:
        {
            "name": "string"
        }

    Returns:
        201: List created successfully
        400: Validation error
        401: Not authenticated
    """
    user_id = session.get('user_id')
    data = request.get_json()

    # Validate required fields
    if not data or not data.get('name'):
        return jsonify({'error': 'List name is required'}), 400

    name = data['name'].strip()

    # Validate name length
    if len(name) < 1:
        return jsonify({'error': 'List name cannot be empty'}), 400

    if len(name) > 200:
        return jsonify({'error': 'List name must be 200 characters or less'}), 400

    # Create new list
    try:
        new_list = TodoList(
            name=name,
            user_id=user_id
        )

        db.session.add(new_list)
        db.session.commit()

        return jsonify({
            'message': 'List created successfully',
            'list': new_list.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create list: {str(e)}'}), 500


@api_bp.route('/lists/<int:list_id>', methods=['PUT'])
@login_required
def update_list(list_id):
    """
    Update a todo list's name.

    Expected JSON body:
        {
            "name": "string"
        }

    Args:
        list_id: ID of the list to update

    Returns:
        200: List updated successfully
        400: Validation error
        401: Not authenticated
        403: Not authorized to update this list
        404: List not found
    """
    user_id = session.get('user_id')
    data = request.get_json()

    # Validate required fields
    if not data or not data.get('name'):
        return jsonify({'error': 'List name is required'}), 400

    name = data['name'].strip()

    # Validate name length
    if len(name) < 1:
        return jsonify({'error': 'List name cannot be empty'}), 400

    if len(name) > 200:
        return jsonify({'error': 'List name must be 200 characters or less'}), 400

    # Find the list
    todo_list = TodoList.query.get(list_id)

    if not todo_list:
        return jsonify({'error': 'List not found'}), 404

    # Check ownership
    if todo_list.user_id != user_id:
        return jsonify({'error': 'Not authorized to update this list'}), 403

    # Update the list
    try:
        todo_list.name = name
        db.session.commit()

        return jsonify({
            'message': 'List updated successfully',
            'list': todo_list.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update list: {str(e)}'}), 500


@api_bp.route('/lists/<int:list_id>', methods=['DELETE'])
@login_required
def delete_list(list_id):
    """
    Delete a todo list and all its todos.

    Args:
        list_id: ID of the list to delete

    Returns:
        200: List deleted successfully
        401: Not authenticated
        403: Not authorized to delete this list
        404: List not found
    """
    user_id = session.get('user_id')

    # Find the list
    todo_list = TodoList.query.get(list_id)

    if not todo_list:
        return jsonify({'error': 'List not found'}), 404

    # Check ownership
    if todo_list.user_id != user_id:
        return jsonify({'error': 'Not authorized to delete this list'}), 403

    # Delete the list (cascade will delete all todos)
    try:
        db.session.delete(todo_list)
        db.session.commit()

        return jsonify({
            'message': 'List deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete list: {str(e)}'}), 500


# ============================================================================
# TODO ROUTES (PR-6 - Top-Level Only)
# ============================================================================

@api_bp.route('/todos/<int:list_id>', methods=['GET'])
@login_required
def get_todos(list_id):
    """
    Get all todos for a specific list (top-level only for PR-6).

    Args:
        list_id: ID of the list to get todos from

    Returns:
        200: List of todos
        401: Not authenticated
        403: Not authorized to access this list
        404: List not found
    """
    user_id = session.get('user_id')

    # Find the list
    todo_list = TodoList.query.get(list_id)

    if not todo_list:
        return jsonify({'error': 'List not found'}), 404

    # Check ownership
    if todo_list.user_id != user_id:
        return jsonify({'error': 'Not authorized to access this list'}), 403

    # Get all top-level todos (parent_id is null)
    todos = TodoItem.query.filter_by(
        list_id=list_id,
        parent_id=None
    ).order_by(TodoItem.created_at).all()

    return jsonify({
        'todos': [todo.to_dict() for todo in todos]
    }), 200


@api_bp.route('/todos', methods=['POST'])
@login_required
def create_todo():
    """
    Create a new top-level todo item (PR-6 - no parent support yet).

    Expected JSON body:
        {
            "list_id": integer,
            "title": "string",
            "description": "string" (optional)
        }

    Returns:
        201: Todo created successfully
        400: Validation error
        401: Not authenticated
        403: Not authorized to add to this list
        404: List not found
    """
    user_id = session.get('user_id')
    data = request.get_json()

    # Validate required fields
    if not data or not data.get('list_id') or not data.get('title'):
        return jsonify({'error': 'list_id and title are required'}), 400

    list_id = data['list_id']
    title = data['title'].strip()
    description = data.get('description', '').strip()

    # Validate title length
    if len(title) < 1:
        return jsonify({'error': 'Title cannot be empty'}), 400

    if len(title) > 500:
        return jsonify({'error': 'Title must be 500 characters or less'}), 400

    # Find the list
    todo_list = TodoList.query.get(list_id)

    if not todo_list:
        return jsonify({'error': 'List not found'}), 404

    # Check ownership
    if todo_list.user_id != user_id:
        return jsonify({'error': 'Not authorized to add to this list'}), 403

    # Create new todo (top-level only - parent_id=None, depth=0)
    try:
        new_todo = TodoItem(
            title=title,
            description=description,
            list_id=list_id,
            user_id=user_id,
            parent_id=None,  # PR-6: Top-level only
            depth=0,
            completed=False,
            collapsed=False
        )

        db.session.add(new_todo)
        db.session.commit()

        return jsonify({
            'message': 'Todo created successfully',
            'todo': new_todo.to_dict()
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

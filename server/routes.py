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

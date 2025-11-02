from flask import Blueprint, request, jsonify, session
from models import db, TodoList, TodoItem, User
from auth import login_required

api_bp = Blueprint('api', __name__, url_prefix='/api')

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
    projects = TodoList.query.filter_by(user_id=user_id).order_by(TodoList.created_at).all()

    return jsonify({
        'projects': [project.to_dict() for project in projects]
    }), 200


@api_bp.route('/projects/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """
    Get a specific project by ID.

    Args:
        project_id: ID of the project to retrieve

    Returns:
        200: Project details
        401: Not authenticated
        403: User doesn't own this project
        404: Project not found
    """
    user_id = session.get('user_id')
    project = TodoList.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    if project.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({
        'project': project.to_dict()
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

    if not data or not data.get('name'):
        return jsonify({'error': 'Project name is required'}), 400

    name = data['name'].strip()

    if len(name) < 1:
        return jsonify({'error': 'Project name cannot be empty'}), 400

    if len(name) > 200:
        return jsonify({'error': 'Project name must be 200 characters or less'}), 400

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

    if not data or not data.get('name'):
        return jsonify({'error': 'Project name is required'}), 400

    name = data['name'].strip()

    if len(name) < 1:
        return jsonify({'error': 'Project name cannot be empty'}), 400

    if len(name) > 200:
        return jsonify({'error': 'Project name must be 200 characters or less'}), 400

    project = TodoList.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    if project.user_id != user_id:
        return jsonify({'error': 'Not authorized to update this project'}), 403

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
    project = TodoList.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    if project.user_id != user_id:
        return jsonify({'error': 'Not authorized to delete this project'}), 403

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
# TODO ROUTES
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

    project = TodoList.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    if project.user_id != user_id:
        return jsonify({'error': 'Not authorized to access this project'}), 403

    todos = TodoItem.query.filter_by(
        list_id=project_id,
        parent_id=None
    ).order_by(TodoItem.created_at).all()

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

    if not data or not data.get('project_id') or not data.get('title'):
        return jsonify({'error': 'project_id and title are required'}), 400

    project_id = data['project_id']
    title = data['title'].strip()
    description = data.get('description', '').strip()
    priority = data.get('priority', 'medium')  # New priority field
    parent_id = data.get('parent_id')  # Now accepting parent_id

    if len(title) < 1:
        return jsonify({'error': 'Title cannot be empty'}), 400

    if len(title) > 500:
        return jsonify({'error': 'Title must be 500 characters or less'}), 400

    project = TodoList.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

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

    if priority not in ['low', 'medium', 'high']:
        priority = 'medium'

    try:
        new_todo = TodoItem(
            title=title,
            description=description,
            priority=priority,
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

    todo = TodoItem.query.get(todo_id)

    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    if todo.user_id != user_id:
        return jsonify({'error': 'Not authorized to update this todo'}), 403

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
            new_completed_state = bool(data['completed'])
            todo.completed = new_completed_state

            # If marking as complete, mark all children as complete too (cascade)
            if new_completed_state:
                def mark_children_complete(parent_todo):
                    for child in parent_todo.children:
                        child.completed = True
                        mark_children_complete(child)  # Recursive

                mark_children_complete(todo)

        if 'collapsed' in data:
            todo.collapsed = bool(data['collapsed'])

        if 'priority' in data:
            priority = data['priority']
            if priority in ['low', 'medium', 'high']:
                todo.priority = priority

        db.session.commit()

        return jsonify({
            'message': 'Todo updated successfully',
            'todo': todo.to_dict(include_children=True)
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

    todo = TodoItem.query.get(todo_id)

    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    if todo.user_id != user_id:
        return jsonify({'error': 'Not authorized to delete this todo'}), 403

    try:
        db.session.delete(todo)
        db.session.commit()

        return jsonify({
            'message': 'Todo deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete todo: {str(e)}'}), 500


@api_bp.route('/todos/<int:todo_id>/move', methods=['POST'])
@login_required
def move_todo(todo_id):
    """
    Move a todo item to a different project.

    Expected JSON body:
        {
            "target_project_id": integer
        }

    Args:
        todo_id: ID of the todo to move

    Returns:
        200: Todo moved successfully
        400: Validation error
        401: Not authenticated
        403: Not authorized to move this todo
        404: Todo or target project not found
    """
    user_id = session.get('user_id')
    data = request.get_json()

    if not data or not data.get('target_project_id'):
        return jsonify({'error': 'target_project_id is required'}), 400

    target_project_id = data['target_project_id']

    todo = TodoItem.query.get(todo_id)

    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    # Check ownership of todo
    if todo.user_id != user_id:
        return jsonify({'error': 'Not authorized to move this todo'}), 403

    # Find the target project
    target_project = TodoList.query.get(target_project_id)

    if not target_project:
        return jsonify({'error': 'Target project not found'}), 404

    # Check ownership of target project
    if target_project.user_id != user_id:
        return jsonify({'error': 'Not authorized to move to this project'}), 403

    if todo.list_id == target_project_id:
        return jsonify({'error': 'Todo is already in this project'}), 400

    # Can only move top-level todos (depth 0, no parent)
    if todo.parent_id is not None:
        return jsonify({'error': 'Only top-level tasks can be moved between projects. Remove from parent first.'}), 400

    try:
        # Recursive function to update list_id for todo and all children
        def update_list_id_recursive(todo_item, new_list_id):
            todo_item.list_id = new_list_id
            for child in todo_item.children:
                update_list_id_recursive(child, new_list_id)

        # Move the todo and all its children
        update_list_id_recursive(todo, target_project_id)

        db.session.commit()

        return jsonify({
            'message': 'Todo moved successfully',
            'todo': todo.to_dict(include_children=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to move todo: {str(e)}'}), 500


@api_bp.route('/todos/<int:todo_id>/reparent', methods=['POST'])
@login_required
def reparent_todo(todo_id):
    """
    Change the parent of a todo (make it a subtask of another todo or move to top-level).
    Can also move to a different project.

    Expected JSON body:
        {
            "new_parent_id": int | null,  # New parent ID (null for top-level)
            "new_project_id": int | null, # Optional: move to different project
            "new_order": int              # Position in new location
        }

    Args:
        todo_id: ID of the todo to reparent

    Returns:
        200: Todo reparented successfully
        400: Validation error
        401: Not authenticated
        403: Not authorized
        404: Todo or parent not found
    """
    user_id = session.get('user_id')
    data = request.get_json()

    todo = TodoItem.query.get(todo_id)

    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    if todo.user_id != user_id:
        return jsonify({'error': 'Not authorized to modify this todo'}), 403

    new_parent_id = data.get('new_parent_id')
    new_project_id = data.get('new_project_id', todo.list_id)
    new_order = data.get('new_order', 0)

    # Validate new_parent if provided
    if new_parent_id is not None:
        new_parent = TodoItem.query.get(new_parent_id)

        if not new_parent:
            return jsonify({'error': 'New parent not found'}), 404

        if new_parent.user_id != user_id:
            return jsonify({'error': 'Not authorized to access new parent'}), 403

        # Prevent circular dependencies
        def is_descendant(potential_ancestor, potential_descendant):
            if potential_ancestor.id == potential_descendant.id:
                return True
            for child in potential_ancestor.children:
                if is_descendant(child, potential_descendant):
                    return True
            return False

        if is_descendant(todo, new_parent):
            return jsonify({'error': 'Cannot make a todo a subtask of itself or its descendants'}), 400

        new_depth = new_parent.depth + 1

        if new_depth > 2:
            return jsonify({'error': 'Maximum nesting depth reached (3 levels max)'}), 400

        def get_max_child_depth(task, current_depth=0):
            if not task.children:
                return current_depth
            return max(get_max_child_depth(child, current_depth + 1) for child in task.children)

        max_child_depth = get_max_child_depth(todo)

        if new_depth + max_child_depth > 2:
            return jsonify({'error': f'Cannot move: task has {max_child_depth} level(s) of subtasks. Moving it here would exceed maximum depth of 3 levels'}), 400
    else:
        new_depth = 0

    # Validate new_project if provided
    if new_project_id != todo.list_id:
        new_project = TodoList.query.get(new_project_id)

        if not new_project:
            return jsonify({'error': 'New project not found'}), 404

        if new_project.user_id != user_id:
            return jsonify({'error': 'Not authorized to access new project'}), 403

    try:
        # Recursive function to update depth and list_id for todo and all children
        def update_hierarchy(todo_item, depth_delta, new_list_id):
            todo_item.depth += depth_delta
            todo_item.list_id = new_list_id
            for child in todo_item.children:
                update_hierarchy(child, depth_delta, new_list_id)

        # Calculate depth delta
        depth_delta = new_depth - todo.depth

        # Update the todo's hierarchy
        todo.parent_id = new_parent_id
        update_hierarchy(todo, depth_delta, new_project_id)

        # Update order
        todo.order_index = new_order

        # Reorder siblings in the new location to make room
        siblings = TodoItem.query.filter_by(
            list_id=new_project_id,
            parent_id=new_parent_id
        ).filter(
            TodoItem.id != todo_id
        ).order_by(TodoItem.order_index).all()

        for sibling in siblings:
            if sibling.order_index >= new_order:
                sibling.order_index += 1

        db.session.commit()

        return jsonify({
            'message': 'Todo reparented successfully',
            'todo': todo.to_dict(include_children=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to reparent todo: {str(e)}'}), 500

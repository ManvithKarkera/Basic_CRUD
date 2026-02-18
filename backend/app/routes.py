from flask import Blueprint, request, jsonify
from app.services import todo_service

api = Blueprint('api', __name__)


@api.route("/", methods=['GET', 'POST'])
def todos_list():
    """
    GET: Retrieve all todos
    POST: Create a new todo
    """
    if request.method == "POST":
        data = request.get_json()
        if not data or 'title' not in data:
            from app.exceptions import ValidationError
            raise ValidationError('Missing required field: title')
        
        title = data['title']
        desc = data.get('desc', '')  # Default to empty string if not provided
        status = data.get('status', 'TODO')
        
        # Service layer handles validation and raises exceptions
        todo = todo_service.create_todo(title, desc, status)
        return jsonify(todo.to_dict()), 201
   
    # GET all todos
    allTodo = todo_service.get_all_todos()
    return jsonify([todo.to_dict() for todo in allTodo]), 200


@api.route("/<int:todo_id>", methods=['GET', 'PUT', 'DELETE'])
def todo_detail(todo_id: int):
    """
    GET: Retrieve a single todo
    PUT: Update a todo (title or status)
    DELETE: Delete a todo
    """
    if request.method == "DELETE":
        # Service layer handles not found error
        todo_service.delete_todo(todo_id)
        return '', 204
    
    if request.method == "PUT":
        data = request.get_json()
        if not data:
            from app.exceptions import ValidationError
            raise ValidationError('Request body is required')
        
        # Check if this is a status update
        if 'status' in data:
            # Service layer handles validation and conflict errors
            todo = todo_service.update_todo_status(todo_id, data['status'])
            return jsonify(todo.to_dict()), 200
        
        # Otherwise, update title (and desc if provided)
        if 'title' in data:
            # Get current todo to preserve desc if not provided
            todo = todo_service.get_todo_by_id(todo_id)
            if not todo:
                from app.exceptions import NotFoundError
                raise NotFoundError('Todo not found')
            
            new_title = data['title']
            new_desc = data.get('desc', todo.desc)  # Preserve existing desc
            
            # Service layer handles validation, not found, and conflict errors
            todo = todo_service.update_todo(todo_id, new_title, new_desc)
            return jsonify(todo.to_dict()), 200
        
        from app.exceptions import ValidationError
        raise ValidationError('No valid fields to update')
    
    # GET request
    todo = todo_service.get_todo_by_id(todo_id)
    if not todo:
        from app.exceptions import NotFoundError
        raise NotFoundError('Todo not found')
    
    return jsonify(todo.to_dict()), 200

from flask import Blueprint, request, jsonify, g
from .controller import get_todos, get_todo_by_id, create_todo, update_todo, delete_todo 
from app import app
from ..middleware.middleware import validate_token, get_current_user

@app.route('/todos', methods=['GET'])
@validate_token
def list_todos():
    todos = get_todos()
    return jsonify([todo for todo in todos]), 200

@app.route('/todos/<todo_id>', methods=['GET'])
@validate_token
def get_todo(todo_id):
    todo = get_todo_by_id(todo_id)
    if todo:
        return jsonify(todo), 200
    return jsonify({"error": "Todo not found"}), 404

@app.route('/todos', methods=['POST'])
@validate_token
def add_todo():
    data = request.json
    todo_id, success = create_todo(data)
    if success:
        return jsonify({"id": todo_id}), 201
    return jsonify({"error": todo_id}), 400

@app.route('/todos/<todo_id>', methods=['PUT'])
@validate_token
def edit_todo(todo_id):
    data = request.json
    updated, success = update_todo(todo_id, data)
    if success:
        if updated:
            return jsonify({"success": True}), 200
        return jsonify({"error": "Todo not found"}), 404
    return jsonify({"error": updated}), 400

@app.route('/todos/<todo_id>', methods=['DELETE'])
@validate_token
def delete_todo_route(todo_id):
    deleted = delete_todo(todo_id)
    if deleted:
        return jsonify({"success": True}), 200
    return jsonify({"error": "Todo not found"}), 404

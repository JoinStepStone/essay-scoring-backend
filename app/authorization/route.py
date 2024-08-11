from flask import Blueprint, request, jsonify, g
from .controller import get_todos, get_todo_by_id, create_todo, update_todo, delete_todo 
from app import app
from ..middleware.middleware import validate_token, get_current_user

@app.route('/login', methods=['POST'])
def login():
    return jsonify({"error": "Todo not found"}), 404

@app.route('/signUp', methods=['POST'])
def get_todo(todo_id):
    todo = get_todo_by_id(todo_id)
    if todo:
        return jsonify(todo), 200
    return jsonify({"error": "Todo not found"}), 404

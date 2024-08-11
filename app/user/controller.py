from bson.objectid import ObjectId
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from app import db
from .model import TodoSchema, UpdateTodoSchema
# Data Access Layer functions

def get_todos():
    todos = db.todos.find()
    return list(todos)

def get_todo_by_id(todo_id):
    todo = db.todos.find_one({"_id": ObjectId(todo_id)})
    return todo

def create_todo(data):
    try:
        # Validate incoming data using Pydantic schema
        todo = TodoSchema(**data)
    except ValidationError as e:
        return {"error": str(e)}, False

    todo_id = db.todos.insert_one(todo.dict()).inserted_id
    return str(todo_id), True

def update_todo(todo_id, data):
    try:
        # Validate incoming data using Pydantic schema
        update_fields = UpdateTodoSchema(**data)
    except ValidationError as e:
        return {"error": str(e)}, False

    update_fields = {k: v for k, v in update_fields.dict().items() if v is not None}

    result = db.todos.update_one(
        {"_id": ObjectId(todo_id)},
        {"$set": update_fields}
    )
    return result.modified_count > 0, True

def delete_todo(todo_id):
    result = db.todos.delete_one({"_id": ObjectId(todo_id)})
    return result.deleted_count > 0

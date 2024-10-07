from flask import request, jsonify
from app import app, db
from ..controller.authorization import (
    signUpController, signInController, getUniListNamesController, verifyEmailAddressController,
    setNewPasswordController
    )
import os
from datetime import datetime
import json
from bson import json_util, Timestamp
from bson.objectid import ObjectId
from ..middleware.middleware import validate_token_duration

@app.route('/', methods=['GET'])
def Home():
    return jsonify({"error": "RUNNING", "code": 400})

@app.route('/uniListNames', methods=['GET'])
def get_uni_list_name():
    response, success, message = getUniListNamesController()
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}

@app.route('/checkAuth', methods=['GET'])
def check_auth():
    response, success, message = validate_token_duration(request)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})

@app.route('/signUp', methods=['POST'])
def signUp():
    data = request.json
    response, success, message = signUpController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})

@app.route('/setNewPassword', methods=['POST'])
def setNewPassword():
    data = request.json
    response, success, message = setNewPasswordController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})

@app.route('/verifyEmailAddress', methods=['POST'])
def verifyEmail():
    data = request.json
    response, success, message = verifyEmailAddressController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    response, success, message = signInController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})

def custom_json_serializer(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, Timestamp):
        return str(obj)
    # Add other non-serializable types here as needed
    raise TypeError(f"Type {type(obj)} not serializable")

@app.route('/test_connection', methods=['GET'])
def test_connection():
    try:
        # Perform a test query to check the connection
        server_status = db.command("serverStatus")
        return jsonify({"status": "Connection successful", "code": 200, "server_info": json.loads(json_util.dumps(server_status))})
    except Exception as e:
        return jsonify({"status": "Connection failed", "code": 500, "error": str(e)})

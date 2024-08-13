from flask import request, jsonify
from app import app
from ..controller.authorization import signUpController, signInController


@app.route('/', methods=['GET'])
def Home():
    return jsonify({"error": "RUNNING", "code": 400})

@app.route('/signUp', methods=['POST'])
def signUp():
    data = request.json
    data = data["data"]
    response, success, message = signUpController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    data = data["data"]
    response, success, message = signInController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})

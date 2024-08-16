from flask import request, jsonify
from app import app, db
from ..controller.authorization import signUpController, signInController


@app.route('/', methods=['GET'])
def Home():
    return jsonify({"error": "RUNNING", "code": 400})

@app.route('/signUp', methods=['POST'])
def signUp():
    data = request.json
    response, success, message = signUpController(data)
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

@app.route('/test_connection', methods=['GET'])
def test_connection():
    try:
        print("\n", "TESTING", "\n")
        # Perform a test query to check the connection
        server_status = db.command("serverStatus")
        return jsonify({"status": "Connection successful", "code": 200, "server_info": server_status})
    except Exception as e:
        return jsonify({"status": "Connection failed", "code": 500, "error": str(e)})

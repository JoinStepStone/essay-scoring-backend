from flask import request, jsonify
import os
from app import app
from ..middleware.middleware import allowed_file, upload_file, validate_token
from ..controller.student import startUserSimulationController, userSimulationController

# Configure upload folder and allowed extensions

@app.route('/student/simulation', methods=['POST'])
def get_all_simulation_of_user():
    data = request.json
    response, success, message = userSimulationController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})

@app.route('/student/simulation/start', methods=['POST'])
@validate_token
def simulation_start():
    data = request.json
    response, success, message = startUserSimulationController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})
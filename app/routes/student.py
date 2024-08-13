from flask import request, jsonify
import os
from app import app
from ..middleware.middleware import allowed_file, upload_file, validate_token
from ..controller.student import updateUserSimulationController, getSimulationSelectedController, simulationSelectionController, simulationByClassCodeController, simulationDetailController

@app.route('/student/classCodeSimulation', methods=['POST'])
@validate_token
def get_simulation_by_class_code():
    data = request.json
    response, success, message = simulationByClassCodeController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})


@app.route('/student/simulation/select', methods=['POST'])
@validate_token
def simulation_selection():
    data = request.json
    response, success, message = simulationSelectionController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})


@app.route('/student/getsimulation/select', methods=['POST'])
@validate_token
def get_simulation_selected():
    data = request.json
    response, success, message = getSimulationSelectedController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})


@app.route('/student/getsimulationDetail', methods=['POST'])
@validate_token
def get_simulation_detail():
    data = request.json
    response, success, message = simulationDetailController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})


@app.route('/student/simulation/upload', methods=['POST'])
@validate_token
def simulation_start():
    if 'file' not in request.files:
        return {'data': '', "code": 400, "message": "No files are found"}
    file = request.files['file']
    if file.filename == '':
        return {'data': '', "code": 400, "message": "No files are found"}

    if file and allowed_file(file.filename):
        filepath = upload_file(file)
        objectData = {
            "status": request.form.get('status'),
            "sharingScore": request.form.get('sharingScore'),
            "grade": request.form.get('grade'),
            "userId": request.form.get('userId'),
            "simulationId": request.form.get('simulationId'),
            "filePath": filepath,
            "startTime": request.form.get('startTime'),
            "endTime": request.form.get('endTime'),
        }
        response, success, message = updateUserSimulationController(objectData)
        if success:
            return {"data": response, "code": 201, "message": message}
    return {"error": response, "code": 400, "message": message}
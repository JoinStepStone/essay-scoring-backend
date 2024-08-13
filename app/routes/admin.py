from flask import request, jsonify
import os
from app import app
from ..middleware.middleware import allowed_file, upload_file, validate_token_admin
from ..controller.admin import createSimulationController, getAllTheStuedents, getAllTheSimulations, getTheSimulationDetails

# Configure upload folder and allowed extensions

@app.route('/admin/getAllStudents', methods=['GET'])
@validate_token_admin
def get_all_students():
    response, success, message = getAllTheStuedents()
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}

@app.route('/admin/getAllSimulations', methods=['GET'])
@validate_token_admin
def get_all_simulations():
    response, success, message = getAllTheSimulations()
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}


@app.route('/admin/uploadFile', methods=['POST'])
@validate_token_admin
def upload_file_route():
    print("upload_file_route",request.files,request.form.get('category'))
    if 'file' not in request.files:
        return {'data': '', "code": 400, "message": "No files are found"}
    file = request.files['file']
    if file.filename == '':
        return {'data': '', "code": 400, "message": "No files are found"}

    if file and allowed_file(file.filename):
        filepath = upload_file(file)
        objectData = {
            "category": request.form.get('category'),
            "simulationName": request.form.get('simulationName'),
            "organizationName": request.form.get('organizationName'),
            "startTime": request.form.get('startTime'),
            "endTime": request.form.get('endTime'),
            "filePath": filepath,
            "classCode": request.form.get('classCode')
        }
        response, success, message = createSimulationController(objectData)
        if success:
            return {"data": response, "code": 201, "message": message}
    return {"error": response, "code": 400, "message": message}

@app.route('/admin/getSimulationDetails', methods=['POST'])
@validate_token_admin
def get_simulation_details():
    data = request.json
    response, success, message = getTheSimulationDetails(data)
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}
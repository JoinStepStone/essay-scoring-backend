from flask import request, jsonify
import os
from app import app
from ..middleware.middleware import allowed_file, upload_file
from ..controller.admin import createSimulationController

# Configure upload folder and allowed extensions


@app.route('/upload', methods=['POST'])
def upload_file_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part', "code": 400, "message": "No files are found"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file part', "code": 400, "message": "No files are found"})

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
            return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})
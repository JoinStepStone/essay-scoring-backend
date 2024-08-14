from flask import request, send_file
import os
from app import app, gridFileStorage
from ..middleware.middleware import allowed_file, upload_file, validate_token_admin
from ..controller.admin import createSimulationController, getAllTheStuedents, getAllTheSimulations, getTheSimulationDetails
from io import BytesIO
from bson import ObjectId

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
        return {"data": response, "code": 201, "message": message }

    return {"error": response, "code": 400, "message": message}


@app.route('/admin/uploadFile', methods=['POST'])
@validate_token_admin
def upload_file_route():
    if 'file' not in request.files:
        return {'data': '', "code": 400, "message": "No files are found"}
    file = request.files['file']
    if file.filename == '':
        return {'data': '', "code": 400, "message": "No files are found"}

    if file and allowed_file(file.filename):
        # filepath = upload_file(file)
        grid_out = gridFileStorage.put(file, filename=file.filename)
        objectData = {
            "category": request.form.get('category'),
            "simulationName": request.form.get('simulationName'),
            "organizationName": request.form.get('organizationName'),
            "startTime": request.form.get('startTime'),
            "endTime": request.form.get('endTime'),
            "fileId": str(grid_out),
            "fileName": file.filename,
            "classCode": request.form.get('classCode')
        }
        response, success, message = createSimulationController(objectData)
        if success:
            return {"data": response, "code": 201, "message": message}
    return {"error": response, "code": 400, "message": message}

@app.route('/admin/downloadSimulationFile', methods=['POST'])
@validate_token_admin  # Optionally, you could validate again here
def download_simulation_file():
    data = request.json
    # Retrieve the file by its ID
    grid_out = gridFileStorage.get(ObjectId(data["file_id"]))
    
    print('\n',data["file_id"],grid_out,'\n')
    if not grid_out:
        return {'data': '', "code": 400, "message": "No files are found"}
    
    # Serve the file
    return send_file(BytesIO(grid_out.read()), mimetype=grid_out.content_type, as_attachment=True, download_name=grid_out.filename)


@app.route('/admin/getSimulationDetails', methods=['POST'])
@validate_token_admin
def get_simulation_details():
    data = request.json
    response, success, message = getTheSimulationDetails(data)
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}
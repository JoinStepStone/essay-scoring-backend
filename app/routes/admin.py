from flask import request, send_file
import os
from app import app, gridFileStorage
from ..middleware.middleware import allowed_file, upload_file, validate_token_admin
from ..controller.admin import createSimulationController, getAllTheStuedents, getAllTheSimulations, getTheSimulationDetails, getStudentById, updateStudentById,getAdminById, updateAdminById, getSimulationById, updateSimulationController
from io import BytesIO
from bson import ObjectId

@app.route('/admin/getSimulationById', methods=['POST'])
@validate_token_admin
def get_simulation_by_Id():
    data = request.json
    response, success, message = getSimulationById(data)
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}

@app.route('/admin/updateAdminById', methods=['POST'])
@validate_token_admin
def update_admin_by_Id():
    data = request.json
    response, success, message = updateAdminById(data)
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}

@app.route('/admin/getAdminById', methods=['GET'])
@validate_token_admin
def get_admin_by_Id():
    response, success, message = getAdminById()
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}

@app.route('/admin/updateStudentById', methods=['POST'])
@validate_token_admin
def update_student_by_Id():
    data = request.json
    response, success, message = updateStudentById(data)
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}

@app.route('/admin/getStudentById', methods=['POST'])
@validate_token_admin
def get_student_by_Id():
    data = request.json
    response, success, message = getStudentById(data)
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}

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


@app.route('/admin/update/uploadFile', methods=['POST'])
@validate_token_admin
def update_uploaded_file_route():
    if 'file' not in request.files:
        return {'data': '', "code": 400, "message": "No files are found"}
    file = request.files['file']
    if file.filename == '':
        return {'data': '', "code": 400, "message": "No files are found"}

    if file and allowed_file(file.filename):
        # Convert file_id from string to ObjectId
        file_id = ObjectId(request.form.get('fileId'))
            
        print("\n", file_id,"\n")
        # Delete the old file
        gridFileStorage.delete(file_id)
        grid_out = gridFileStorage.put(file, filename=file.filename)
        objectData = {
            "_id": request.form.get('_id'),
            "category": request.form.get('category'),
            "simulationName": request.form.get('simulationName'),
            "organizationName": request.form.get('organizationName'),
            "startTime": request.form.get('startTime'),
            "endTime": request.form.get('endTime'),
            "classCode": request.form.get('classCode'),
            "fileId": str(grid_out),
            "fileName": file.filename,
            "participants": request.form.get('participants')
        }
        response, success, message = updateSimulationController(objectData)
        if success:
            return {"data": response,  "code": 201, "message": message}

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

@app.route('/admin/downloadSimulationFile/<file_id>', methods=['GET'])
# @validate_token_admin  # Optionally, you could validate again here
def download_simulation_file(file_id):
    # Retrieve the file by its ID
    grid_out = gridFileStorage.get(ObjectId(file_id))
    
    print('\n',id,grid_out,'\n')
    if not grid_out:
        return {'data': '', "code": 400, "message": "No files are found"}
    
    # Serve the file as a download
    return send_file(
        BytesIO(grid_out.read()), 
        mimetype=grid_out.content_type, 
        as_attachment=True, 
        download_name=grid_out.filename
    )


@app.route('/admin/getSimulationDetails', methods=['POST'])
@validate_token_admin
def get_simulation_details():
    data = request.json
    response, success, message = getTheSimulationDetails(data)
    if success:
        return {"data": response, "code": 201, "message": message}

    return {"error": response, "code": 400, "message": message}
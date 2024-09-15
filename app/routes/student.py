from flask import request, send_file, jsonify
from bson import ObjectId
from app import app, gridFileStorage, simulation_database
from io import BytesIO
from ..middleware.middleware import (
    allowed_file, 
    upload_file, validate_token, 
    parsed_xlsx_get_score, remove_sheets, compare_results,
    get_df, paste_extracted_df, copy_sheet, fill_values_get_score
    )
from ..controller.student import (
    updateUserSimulationController, 
    getSimulationSelectedController, 
    simulationSelectionController, 
    simulationByClassCodeController, 
    simulationDetailController,
    getMeController,
    updateMeController,
    deleteFileController,
    updateSharingScoreController
    )


@app.route('/student/simulation/score', methods=['POST']) 
@validate_token
def get_simulation_student_score():
    if 'file' not in request.files:
        return {'data': '', "code": 400, "message": "No files are found"}
    file = request.files['file']
    original_file_id = request.form.get('original_file_id')

    if file.filename == '':
        return {'data': '', "code": 400, "message": "No files are found"}

    grid_out = gridFileStorage.get(ObjectId(original_file_id))
    if not grid_out:
        return {'data': '', "code": 400, "message": "No files are found"}

    grid_out_in_bytes = BytesIO(grid_out.read())
    copy_sheet(grid_out_in_bytes, file)
    response, success, message = fill_values_get_score("student_file", file)
    if success:
        return {"data": response, "code": 201, "message": message}
        
    return jsonify({"error": response, "code": 400, "message": message})
    

@app.route('/student/updateSharingScore', methods=['POST'])
@validate_token
def update_sharing_score_handler():
    data = request.json
    response, success, message = updateSharingScoreController(data)
    if success:
        return {"data": response, "code": 201, "message": message}
        
    return jsonify({"error": response, "code": 400, "message": message})

@app.route('/student/fileDeleteHandler', methods=['POST'])
@validate_token
def delete_file_handler():
    data = request.json
    response, success, message = deleteFileController(data)
    if success:
        return {"data": response, "code": 201, "message": message}
        
    return jsonify({"error": response, "code": 400, "message": message})

@app.route('/student/updateMe', methods=['POST'])
@validate_token
def update_me():
    data = request.json
    response, success, message = updateMeController(data)
    if success:
        return {"data": response, "code": 201, "message": message}
    return jsonify({"error": response, "code": 400, "message": message})

@app.route('/student/getMe', methods=['POST'])
@validate_token
def get_Me():
    data = request.json
    response, success, message = getMeController(data)
    if success:
        return jsonify({"data": response, "code": 201, "message": message})
    return jsonify({"error": response, "code": 400, "message": message})

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


@app.route('/student/downloadSimulationFile/<file_id>', methods=['GET']) 
# @validate_token
def download_simulation_file_student(file_id):
    simulationId = file_id.split(",")[0]
    file_id = file_id.split(",")[1]

    simulations = list(simulation_database.find(
            {"_id": ObjectId(simulationId), "status": False}
        ))

    if simulations:
        return jsonify({"data": "", "code": 400, "message": "Simulation is inactive"})

    grid_out = gridFileStorage.get(ObjectId(file_id))
    if not grid_out:
        return {'data': '', "code": 400, "message": "No files are found"}
    
    file_in_bytes = remove_sheets(BytesIO(grid_out.read()))
    # Serve the file as a download
    return send_file(
        file_in_bytes, 
        mimetype=grid_out.content_type, 
        as_attachment=True, 
        download_name=grid_out.filename
    )

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
        # # filepath = upload_file(file)
        grid_out = gridFileStorage.put(file, filename=file.filename)
        objectData = {
            "status": request.form.get('status'),
            "sharingScore": request.form.get('sharingScore'),
            "grade": request.form.get('grade'),
            "userId": request.form.get('userId'),
            "simulationId": request.form.get('simulationId'),
            "fileId": str(grid_out),
            "fileName": file.filename,
            "startTime": request.form.get('startTime'),
            "endTime": request.form.get('endTime'),
        }
        response, success, message = updateUserSimulationController(objectData)
        if success:
            return {"data": response, "code": 201, "message": message}
        return {"error": response, "code": 400, "message": message}
from flask import request, jsonify
import os
from app import app
from ..controller.authorization import signUpController, signInController
from ..middleware.middleware import allowed_file

# Configure upload folder and allowed extensions


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Accessing other form data
        string_field = request.form.get('stringField')

        # Process the string_field and file here
        return jsonify({'message': 'File successfully uploaded', 'file_path': filepath, 'string_field': string_field}), 200

    return jsonify({'error': 'File type not allowed'}), 400
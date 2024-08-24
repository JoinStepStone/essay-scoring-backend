import jwt
from flask import request, jsonify, g
from functools import wraps
from app import user_database, app
import datetime
import os
import openpyxl
from openpyxl.styles import Font, PatternFill
import pandas as pd
from openpyxl.styles.colors import Color

# Secret key for JWT encoding/decoding
SECRET_KEY = "your_secret_key_here"
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def get_cell_value(file, sheet_name, cell):
    
    df = pd.read_excel(file, sheet_name=sheet_name, header=None)
    
    column_letter = cell[0]  
    row_number = int(cell[1:]) - 1
    
    # Convert column letter to a zero-based index
    column_index = ord(column_letter.upper()) - ord('A')
    
    # Retrieve the value from the DataFrame
    cell_value = df.iloc[row_number, column_index]
    
    return cell_value

def make_dict_grading_key(value_list):
    if len(value_list[0]) == len(value_list[1]) == len(value_list[2]):
        dictionary_grading_list = []
        value_list[0].pop(0)
        value_list[1].pop(0)
        value_list[2].pop(0)

        for cell_value1, cell_value2, cell_value3 in zip(value_list[0], value_list[1], value_list[2]):
            try:
                if isinstance(cell_value1, str):
                    cell_value_cleaned = cell_value1.strip("=")
                    file_name, cell_reference = cell_value_cleaned.split('!')
                    file_name_clean = file_name.strip("'")
                    parts = file_name_clean.split('_')
                    parts[1] = "Student"
                    modified_string = '_'.join(parts)
                    dictionary_grading_list.append({
                        "file_name" : file_name_clean,
                        "cell_number" : cell_reference,
                        "cell_value": cell_value2,
                        "grade": cell_value3,
                        "target_file_name": modified_string
                    })
            except:
                print("\n", cell_value1, cell_value2, cell_value3)
                return "", False, "Error in processing"

        return dictionary_grading_list, True, ""

    return "", False, "Grading Key Workbook has different length of cell, values and grades"

def remove_unnessary_data(grading_key_df):
    # Drop rows where all elements are NaN and drop columns that are entirely NaN
    grading_key_df.dropna(how='all', inplace=True)
    grading_key_df.dropna(axis=1, how='all', inplace=True)
    
    # Convert to dictionary format
    grading_key_dict = grading_key_df.to_dict(orient='list')

    return grading_key_dict

def parsed_xlsx_get_score(file):
    # Load the Excel file
    xlsx = pd.ExcelFile(file)
    
    # Check if 'Grading Key' sheet exists
    if 'Grading Key' in xlsx.sheet_names:
        # Parse the 'Grading Key' sheet
        grading_key_df = pd.read_excel(file, sheet_name='Grading Key')
        cleaned_original_data = remove_unnessary_data(grading_key_df)
        dictionary_grading_key, success, error = make_dict_grading_key(list(cleaned_original_data.values()))

        print("\n", get_cell_value(file, "Toggle Model_Student", "H14"), "\n")
        
        return dictionary_grading_key, success, error
    else:
        return "", False, "Grading Key sheet not found in the Excel file."


def upload_file(file):
    fileDummy = file.filename.rsplit('.', 1)[0]
    extension = file.filename.rsplit('.', 1)[1]
    filename = fileDummy + str(datetime.datetime.utcnow()) + "." + extension
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Process the string_field and file here
    return filepath

def generate_access_token(info, expires_in="12h"):
    # Convert expires_in to seconds (12 hours = 43200 seconds)
    if expires_in == "12h":
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    else:
        raise ValueError("Unsupported expiration format")

    # Generate the JWT
    token = jwt.encode(
        {"info": info, "exp": expiration},
        SECRET_KEY,
        algorithm="HS256"
    )

    return token

def validate_token_duration(request):
    try:
        # Extract the token from the Authorization header
        auth_header = request.headers.get('Authorization', None)
        if auth_header is None:
            return {"data": "", "code": 401, "message": "Header does not have token"}

        token = auth_header.split(" ")[1]
        
        # Decode the JWT token
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return "", False, "Token has been expired"
        except jwt.InvalidTokenError:
            return "", False, "Token is invalid"

        return "", True, "Token is valid"
    except Exception as e:
        return "",False, str(e)

def validate_token_admin(f):
    @wraps(f)
    def decorated_function_admin(*args, **kwargs):
        try:
            # Extract the token from the Authorization header
            auth_header = request.headers.get('Authorization', None)
            if auth_header is None:
                return {"data": "", "code": 401, "message": "Header does not have token"}

            token = auth_header.split(" ")[1]
            
            # Decode the JWT token
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return {"data": "", "code": 401, "message": "Token has been expired"}
            except jwt.InvalidTokenError:
                return {"data": "", "code": 401, "message": "Token is invalid"}

            # Find the user in the database
            user = user_database.find_one({"email": data['info']["email"], "role": "Admin"})
            if not user:
                return {"data": "", "code": 401, "message": "User is not found"}

            # Attach user info to the global `g` object
            g.current_user = {
                "email": user["email"],
                "role": user["role"],
                "_id": str(user["_id"]),
                "name": user.get("name")
            }

            return f(*args, **kwargs)
        except Exception as e:
            return {"data": "", "code": 401, "message": str(e)}

    return decorated_function_admin

def validate_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Extract the token from the Authorization header
            auth_header = request.headers.get('Authorization', None)
            if auth_header is None:
                return {"data": "", "code": 401, "message": "Header does not have token"}

            token = auth_header.split(" ")[1]

            # Decode the JWT token
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return {"data": "", "code": 401, "message": "Token has been expired"}
            except jwt.InvalidTokenError:
                return {"data": "", "code": 401, "message": "Token is invalid"}

            # Find the user in the database
            user = user_database.find_one({"email": data['info']["email"], "role": "Student"})
            if not user:
                return {"data": "", "code": 401, "message": "User is not found"}

            # Attach user info to the global `g` object
            g.current_user = {
                "email": user["email"],
                "role": user["role"],
                "_id": str(user["_id"]),
                "name": user.get("name")
            }

            return f(*args, **kwargs)
        except Exception as e:
            return {"data": "", "code": 401, "message": str(e)}

    return decorated_function

# Function to get the current user from `g`
def get_current_user():
    return getattr(g, "current_user", None)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


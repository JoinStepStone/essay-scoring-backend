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
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}

def save_parsed_data_to_excel(parsed_data, output_file_path):
    wb = openpyxl.Workbook()
    for sheet_name, sheet_data in parsed_data.items():
        ws = wb.create_sheet(title=sheet_name)
        for row_idx, row in enumerate(sheet_data):
            for col_idx, cell_data in enumerate(row):
                cell = ws.cell(row=row_idx + 1, column=col_idx + 1, value=cell_data["value"])
                
                # Set font properties
                if cell_data["font"]:
                    font_color = None
                    if cell_data["font"]["color"]:
                        if isinstance(cell_data["font"]["color"], str):
                            font_color = Color(rgb=cell_data["font"]["color"])
                        elif hasattr(cell_data["font"]["color"], 'rgb'):
                            font_color = Color(rgb=cell_data["font"]["color"].rgb)
                    
                    cell.font = Font(
                        name=cell_data["font"]["name"],
                        size=cell_data["font"]["size"],
                        bold=cell_data["font"]["bold"],
                        italic=cell_data["font"]["italic"],
                        color=font_color
                    )
                
                # Set fill properties
                if cell_data["fill"]:
                    fill_color = None
                    if cell_data["fill"]["bgColor"]:
                        if isinstance(cell_data["fill"]["bgColor"], str):
                            fill_color = Color(rgb=cell_data["fill"]["bgColor"])
                        elif hasattr(cell_data["fill"]["bgColor"], 'rgb'):
                            fill_color = Color(rgb=cell_data["fill"]["bgColor"].rgb)
                    
                    # Only set fill if color is available
                    if fill_color:
                        cell.fill = PatternFill(
                            fill_type=cell_data["fill"]["fill_type"],
                            fgColor=fill_color
                        )

    wb.save(output_file_path)

def parse_csv(file_path):
    df = pd.read_csv(file_path)
    return df.to_dict(orient='records')

def parse_excel(file_path):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    all_data = {}
    for sheet in wb.sheetnames:
        sheet_data = []
        ws = wb[sheet]
        for row in ws.iter_rows():
            row_data = []
            for cell in row:
                cell_info = {
                    "value": cell.value,
                    "font": {
                        "name": cell.font.name, 
                        "size": cell.font.size,
                        "bold": cell.font.bold,
                        "italic": cell.font.italic,
                        "color": cell.font.color.rgb if cell.font.color else None
                    },
                    "fill": {
                        "fill_type": cell.fill.fill_type,
                        "bgColor": cell.fill.bgColor.rgb if cell.fill.bgColor else None
                    }
                }
                row_data.append(cell_info)
            sheet_data.append(row_data)
        all_data[sheet] = sheet_data
    return all_data

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


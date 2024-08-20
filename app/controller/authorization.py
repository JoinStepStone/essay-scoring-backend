from pydantic import ValidationError
from app import user_database, name_storage_database
from ..models.user import UserSchema
from ..middleware.middleware import generate_access_token

def getUniListNamesController():
    try:

        # Check if the user with the same email already exists
        universitiesList = list(name_storage_database.find({}, { "id" : 0, "category": 0, "simulationName": 0, "organizationName": 0 }))
        universitiesList[0]["_id"] = str(universitiesList[0]["_id"])

        return universitiesList[0], True, "Fetched Successfully"

    except ValidationError as e:
        return str(e), False, "Something went bad"

def signUpController(data):
    try:

        # Validate incoming data using Pydantic schema
        user = UserSchema(**data)

        # Check if the user with the same email already exists
        existing_user = user_database.find_one({"email": user.email})
        if existing_user:
            return "", False, "User with this email already exists"

        result = user_database.insert_one(user.dict())

        if result:
            return "", True, "Signed up successfully"
    except ValidationError as e:
        return str(e), False, "Something went bad"


def signInController(data):
    try:
        user = data
        # Check if the user with the same email already exists
        existing_user = user_database.find_one({"email": user["email"], "password": user["password"] })
        if existing_user:
            existing_user['_id'] = str(existing_user['_id'])
            tokenized = generate_access_token(existing_user)
            return {"token":tokenized,"role":existing_user["role"],"_id":existing_user['_id']}, True, "Signed in successfully"

        return "", False, "User does not exist"
    except ValidationError as e:
        return str(e), False, "Something went bad"



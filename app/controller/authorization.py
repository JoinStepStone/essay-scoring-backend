from pydantic import ValidationError
from app import db
from ..models.user import UserSchema
from ..middleware.middleware import generate_access_token

def signUpController(data):
    try:
        # Validate incoming data using Pydantic schema
        user = UserSchema(**data)

        # Check if the user with the same email already exists
        existing_user = db.user.find_one({"email": user.email})
        if existing_user:
            return "", False, "User with this email already exists"

        result = db.user.insert_one(user.dict())
        # Retrieve the inserted document using the inserted_id
        inserted_user = db.user.find_one({"_id": result.inserted_id})

        # Return the inserted document as a dictionary, converting the ObjectId to a string
        if result:
            inserted_user['_id'] = str(inserted_user['_id'])
            tokenized = generate_access_token(inserted_user)
            return "", True, "Signed up successfully"
    except ValidationError as e:
        return str(e), False, "Something went bad"


def signInController(data):
    try:
        user = data
    
        # Check if the user with the same email already exists
        existing_user = db.user.find_one({"email": user["email"]})
        if existing_user:
            existing_user['_id'] = str(existing_user['_id'])
            tokenized = generate_access_token(existing_user)
            return str(tokenized), True, "Signed in successfully"

        return "", False, "User does not exist"
    except ValidationError as e:
        return str(e), False, "Something went bad"



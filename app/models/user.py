from bson.objectid import ObjectId
from pydantic import BaseModel, Field, ValidationError, EmailStr
from typing import Optional 
from app import db

# Define Pydantic schemas

class UserSchema(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    university: str
    gradYear: str
    ethnicity: str
    race: str
    gender: str

    class Config:
        # This allows using MongoDB ObjectId fields with Pydantic
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
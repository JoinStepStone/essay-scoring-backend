from bson.objectid import ObjectId
from pydantic import BaseModel, Field, ValidationError, EmailStr
from typing import Optional 
from app import db

class UserSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    firstName: str
    lastName: str
    email: EmailStr
    password: Optional[str] = None
    university: str
    gradYear: str
    ethnicity: str
    race: str
    gender: str
    role: str = "Student"

    class Config:
        # This allows using MongoDB ObjectId fields with Pydantic
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
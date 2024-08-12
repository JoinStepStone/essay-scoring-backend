from bson.objectid import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError, EmailStr
from typing import Optional 
from mongoengine import Document, StringField, ReferenceField, FloatField
from .user import UserSchema
from .simulation import SimulationSchema

class UserSimulationSchema(BaseModel):
    status: bool = False
    sharingScore: Optional[bool]  = None
    grade: Optional[str] = None
    userId: str 
    simulationId: str 

    class Config:
        # This allows using MongoDB ObjectId fields with Pydantic
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


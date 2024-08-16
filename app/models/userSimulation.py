from bson.objectid import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError, EmailStr, root_validator
from typing import Optional 
from mongoengine import Document, StringField, ReferenceField, FloatField
from .user import UserSchema
from .simulation import SimulationSchema
from dateutil import parser

class UserSimulationSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    status: Optional[bool] = False
    sharingScore: Optional[bool]  = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    duration: Optional[str] = None  
    grade: Optional[str] = None
    fileId: Optional[str] = None
    fileName: Optional[str] = None
    userId: str 
    simulationId: str 

    @root_validator(pre=True)
    def calculate_duration(cls, values):
        start_time = values.get('startTime')
        end_time = values.get('endTime')
        
        # Parse startTime and endTime if they are strings
        if isinstance(start_time, str):
            start_time = parser.parse(start_time)
            values['startTime'] = start_time  # Update the values with parsed datetime
        
        if isinstance(end_time, str):
            end_time = parser.parse(end_time)
            values['endTime'] = end_time  # Update the values with parsed datetime
        
        # Calculate duration if both startTime and endTime are present
        if start_time and end_time:
            duration = end_time - start_time
            values['duration'] = str(duration)  # Convert timedelta to string
        
        return values


    class Config:
        # This allows using MongoDB ObjectId fields with Pydantic
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


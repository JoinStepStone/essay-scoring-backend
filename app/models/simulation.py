from bson.objectid import ObjectId
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, ValidationError, EmailStr, root_validator
from typing import Optional 
from app import db

class SimulationSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    category: str
    simulationName: str
    organizationName: str
    startTime: datetime
    endTime: datetime
    duration: Optional[str] = None  # Store duration as a string
    filePath: str
    classCode: str
    status: bool = True
    participants: int = 0

    @root_validator(pre=True)
    def calculate_duration(cls, values):
        start_time = values.get('startTime')
        end_time = values.get('endTime')
        if start_time and end_time:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)
            
            duration = end_time - start_time
            values['duration'] = str(duration)  # Convert timedelta to string
        return values

    class Config:
        # This allows using MongoDB ObjectId fields with Pydantic
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            timedelta: lambda v: str(v) 
        }
    # description: Optional[str] = None


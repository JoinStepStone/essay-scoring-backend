from bson.objectid import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError, EmailStr
from typing import Optional 
from app import db

# Define Pydantic schemas

class SimulationSchema(BaseModel):
    category: str
    simulationName: str
    organizationName: str
    startTime: datetime
    endTime: datetime
    filePath: str
    classCode: str
    status: bool = True
    participants: int = 0

    class Config:
        # This allows using MongoDB ObjectId fields with Pydantic
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
    # description: Optional[str] = None


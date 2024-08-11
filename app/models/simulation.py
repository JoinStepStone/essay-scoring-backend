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

    # description: Optional[str] = None


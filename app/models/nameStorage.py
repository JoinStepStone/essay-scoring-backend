from bson.objectid import ObjectId
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, ValidationError, EmailStr, root_validator
from typing import Optional 
from app import db

class NameStorageSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    category: Optional[list[str]] = None
    simulationName: Optional[list[str]] = None
    organizationName: Optional[list[str]] = None

    class Config:
        # This allows using MongoDB ObjectId fields with Pydantic
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
        }
    # description: Optional[str] = None


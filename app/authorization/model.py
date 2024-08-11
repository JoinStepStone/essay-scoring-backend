from bson.objectid import ObjectId
from pydantic import BaseModel, Field, ValidationError
from typing import Optional 
from app import db

# Define Pydantic schemas

class UserSchema(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)

class ProductSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


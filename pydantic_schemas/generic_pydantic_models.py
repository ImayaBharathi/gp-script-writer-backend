from pydantic import BaseModel, EmailStr
from typing import List, Union
import uuid

class CustomResponse(BaseModel):
    success: bool
    message: str
    data: list
    class Config:
        json_schema_extra = {
            "success" : "true or false",
            "message" : "response message",
            "data" : "data from BE"
        }
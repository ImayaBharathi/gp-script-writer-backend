from pydantic import BaseModel
import uuid

class ScriptBase(BaseModel):
    title: str
    genre: str
    logline: str
    user_id: uuid.UUID

class ScriptCreate(ScriptBase):
    pass

class Script(ScriptBase):
    script_id: uuid.UUID

    class Config:
        from_attributes = True

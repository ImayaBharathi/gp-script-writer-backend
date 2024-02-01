from pydantic import BaseModel
import uuid
from typing import Optional


class ScriptBase(BaseModel):
    title: str
    genre: str
    logline: str
    # user_id: uuid.UUID

class ScriptCreate(ScriptBase):
    pass

class Script(ScriptBase):
    script_id: uuid.UUID

    class Config:
        from_attributes = True


# Schema for creating a new ScriptNote
class ScriptNoteCreate(BaseModel):
    note_id: int
    script_id: uuid.UUID
    user_id: uuid.UUID
    note_content: str


class ScriptNote(BaseModel):
    note_id: int
    script_id: uuid.UUID
    user_id: uuid.UUID
    note_content: str

    class Config:
        from_attributes = True


# Schema for ScriptNote response
# class ScriptNote(BaseModel):
#     note_id: uuid.UUID
#     script_id: uuid.UUID
#     user_id: uuid.UUID
#     note_content: str

#     class Config:
#         from_attributes = True


import uuid
from pydantic import BaseModel
from typing import List

class ScriptVersionBase(BaseModel):
    script_id: uuid.UUID
    content: str
    change_summary: str
    modified_by: uuid.UUID

class ScriptVersionCreate(ScriptVersionBase):
    pass

class ScriptVersion(ScriptVersionBase):
    version_id: uuid.UUID
    script_file_url: str

    class Config:
        from_attributes = True

class ScriptVersionsListResponse(BaseModel):
    versions: List[ScriptVersion]

    class Config:
        from_attributes = True

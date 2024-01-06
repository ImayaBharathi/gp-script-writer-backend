##### Fastapi Imports

from fastapi import APIRouter, Depends, HTTPException

##### Database Models & SQLAlchemy Imports
from sqlalchemy.orm import Session
from db_models.db_setup import get_db
from datetime import datetime
import uuid
from typing import List

##### Pydantic Imports
from pydantic_schemas.script_pydantic_models import Script, ScriptCreate, ScriptNote, ScriptNoteCreate
from pydantic_schemas.user_pydantic_models import UserCreate

##### Utils Imports
from .api_utils import script_utils
from .api_utils import user_utils

router = APIRouter()

@router.post("/scripts", tags=["Scripts"], response_model=Script)
def create_script(
    scripts: ScriptCreate,
    # Other script-related parameters here as needed
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    last_modified_at = datetime.utcnow()
    new_script = script_utils.create_script(db, scripts.title, scripts.genre, scripts.user_id, scripts.logline,last_modified_at)
    return new_script

@router.get("/scripts/{script_id}", tags=["Scripts"], response_model=Script)
def read_script(
    script_id: int,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    script = script_utils.get_script(db, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script

@router.put("/scripts/{script_id}", tags=["Scripts"], response_model=Script)
def update_script(
    script_id: uuid.UUID,
    scripts: ScriptCreate,    # Other script-related parameters here as needed
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    last_modified_at = datetime.utcnow()
    updated_script = script_utils.update_script(db, script_id, scripts.title, scripts.genre, scripts.user_id, scripts.logline,last_modified_at)
    if not updated_script:
        raise HTTPException(status_code=404, detail="Script not found")
    return updated_script

@router.delete("/scripts/{script_id}", tags=["Scripts"])
def delete_script(
    script_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    deleted = script_utils.delete_script(db, script_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Script not found")
    return {"message": "Script deleted successfully"}

############# For script notes
@router.post("/script_notes/", response_model=ScriptNote, tags=["Script Notes"])
def create_script_note(script_note: ScriptNoteCreate, 
                       db: Session = Depends(get_db),
                       current_user: UserCreate = Depends(user_utils.get_current_user)):
    return script_utils.create_script_note(db=db, script_note=script_note)

# Get all ScriptNotes for a Script
@router.get("/script_notes/{script_id}", response_model=List[ScriptNote], tags=["Script Notes"])
def get_script_note(script_id: uuid.UUID, 
                     db: Session = Depends(get_db),
                     current_user: UserCreate = Depends(user_utils.get_current_user)):
    return script_utils.get_script_notes_by_script_id(db=db, script_id=script_id)

# Update ScriptNote
@router.put("/script_notes/{note_id}", response_model=ScriptNote, tags=["Script Notes"])
def update_script_note(note_id: int, note_content: str, 
                       db: Session = Depends(get_db),
                       current_user: UserCreate = Depends(user_utils.get_current_user)):
    db_note = script_utils.get_script_note_by_id(db=db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="ScriptNote not found")
    return script_utils.update_script_note(db=db, db_note=db_note, note_content=note_content)

# Delete ScriptNote
@router.delete("/script_notes/{note_id}", tags=["Script Notes"])
def delete_script_note(note_id: int, 
                       db: Session = Depends(get_db), 
                       current_user: UserCreate = Depends(user_utils.get_current_user)):
    db_note = script_utils.get_script_note_by_id(db=db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="ScriptNote not found")
    return script_utils.delete_script_note(db=db, db_note=db_note)

# # Get all ScriptNotes for a Script
# @router.get("/script_notes/{script_id}/notes", response_model=List[ScriptNote], tags=["Script Notes"])
# def get_script_notes(script_id: uuid.UUID, 
#                      db: Session = Depends(get_db),
#                      current_user: UserCreate = Depends(user_utils.get_current_user)):
#     return script_utils.get_script_notes_by_script_id(db=db, script_id=script_id)

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
from pydantic_schemas.generic_pydantic_models import CustomResponse

##### Utils Imports
from .api_utils import script_utils
from .api_utils import user_utils

from loguru import logger

router = APIRouter()

@router.post("/scripts", tags=["Scripts"], response_model=CustomResponse)
def create_script(
    scripts: ScriptCreate,
    # Other script-related parameters here as needed
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    last_modified_at = datetime.utcnow()
    new_script = script_utils.create_script(db, scripts.title, scripts.genre, scripts.user_id, scripts.logline,last_modified_at)
    new_script = vars(new_script)
    new_script.pop('_sa_instance_state')
    success = True
    message = "Script Created"
    return CustomResponse(success=success, message=message, data=[new_script])
    # return new_script

@router.get("/scripts/{script_id}", tags=["Scripts"], response_model=CustomResponse)
def get_script_from_script_id(
    script_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    script = script_utils.get_script(db, script_id)
    if not script:
        return CustomResponse(success=False, message="Script not found", data=[])
        # raise HTTPException(status_code=404, detail="Script not found")
    script = vars(script)
    script.pop('_sa_instance_state')
    success = True
    message = "Script Fetched"
    return CustomResponse(success=success, message=message, data=[script])
    # return script

@router.get("/scripts/all/", tags=["Scripts"], response_model=CustomResponse)
def return_all_scripts(
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    script = script_utils.get_all_script(db, current_user.user_id)
    if not script:
        return CustomResponse(success=False, message="Script not found", data=[])
        # raise HTTPException(status_code=404, detail="No scripts found")
    logger.info(script)
    scripts = []
    for scpt in script:
        scpt_ = vars(scpt)
        scpt_.pop('_sa_instance_state')
        scripts.append(scpt_)
    success = True
    message = "Scripts Fetched"
    return CustomResponse(success=success, message=message, data=scripts)
    # return script

@router.put("/scripts/{script_id}", tags=["Scripts"], response_model=CustomResponse)
def update_script(
    script_id: uuid.UUID,
    scripts: ScriptCreate,    # Other script-related parameters here as needed
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    last_modified_at = datetime.utcnow()
    updated_script = script_utils.update_script(db, script_id, scripts.title, scripts.genre, scripts.user_id, scripts.logline,last_modified_at)
    if not updated_script:
        return CustomResponse(success=False, message="Script not found", data=[])
        # raise HTTPException(status_code=404, detail="Script not found")
    updated_script = vars(updated_script)
    updated_script.pop('_sa_instance_state')
    success = True
    message = "Script Updated"
    return CustomResponse(success=success, message=message, data=[updated_script])
    # return updated_script

@router.delete("/scripts/{script_id}", tags=["Scripts"], response_model=CustomResponse)
def delete_script(
    script_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    deleted = script_utils.delete_script(db, script_id)
    if not deleted:
        return CustomResponse(success=False, message="Script not found", data=[])
        # raise HTTPException(status_code=404, detail="Script not found")
    success = True
    message = "Script Deleted"
    return CustomResponse(success=success, message=message, data=[])
    # return {"message": "Script deleted successfully"}

############# For script notes
@router.post("/script_notes/", tags=["Script Notes"], response_model=CustomResponse)
def create_script_note(script_note: ScriptNoteCreate, 
                       db: Session = Depends(get_db),
                       current_user: UserCreate = Depends(user_utils.get_current_user)):
    
    script_notes = script_utils.create_script_note(db=db, script_note=script_note)
    script_notes = vars(script_notes)
    script_notes.pop('_sa_instance_state')
    success = True
    message = "Script Notes created"
    return CustomResponse(success=success, message=message, data=[script_notes])
    # return 
    

# Get all ScriptNotes for a Script
@router.get("/script_notes/{script_id}", tags=["Script Notes"], response_model=CustomResponse)
def get_script_note(script_id: uuid.UUID, 
                     db: Session = Depends(get_db),
                     current_user: UserCreate = Depends(user_utils.get_current_user)):
    
    script_notes = script_utils.get_script_notes_by_script_id(db=db, script_id=script_id)
    script_notes_= []
    for scpt in script_notes:
        scpt_ = vars(scpt)
        scpt_.pop('_sa_instance_state')
        script_notes_.append(scpt_)
    success = True
    message = "Script Notes fetched"
    return CustomResponse(success=success, message=message, data=script_notes_)
    # return 

# Update ScriptNote
@router.put("/script_notes/{note_id}", tags=["Script Notes"], response_model=CustomResponse)
def update_script_note(note_id: int, note_content: str, 
                       db: Session = Depends(get_db),
                       current_user: UserCreate = Depends(user_utils.get_current_user)):
    db_note = script_utils.get_script_note_by_id(db=db, note_id=note_id)
    if db_note is None:
        return CustomResponse(success=False, message="Script Note not found", data=[])
        # raise HTTPException(status_code=404, detail="ScriptNote not found")
    script_notes = script_utils.update_script_note(db=db, db_note=db_note, note_content=note_content)
    script_notes = vars(script_notes)
    script_notes.pop('_sa_instance_state')
    success = True
    message = "Script Notes updated"
    return CustomResponse(success=success, message=message, data=[script_notes])


# Delete ScriptNote
@router.delete("/script_notes/{note_id}", tags=["Script Notes"], response_model=CustomResponse)
def delete_script_note(note_id: int, 
                       db: Session = Depends(get_db), 
                       current_user: UserCreate = Depends(user_utils.get_current_user)):
    db_note = script_utils.get_script_note_by_id(db=db, note_id=note_id)
    if db_note is None:
        return CustomResponse(success=False, message="Script Note not found", data=[])
        # raise HTTPException(status_code=404, detail="ScriptNote not found")
    delete_status = script_utils.delete_script_note(db=db, db_note=db_note)
    if delete_status:
        success = True
        message = "Script Notes deleted"
        return CustomResponse(success=success, message=message, data=[])


# # Get all ScriptNotes for a Script
# @router.get("/script_notes/{script_id}/notes", response_model=List[ScriptNote], tags=["Script Notes"])
# def get_script_notes(script_id: uuid.UUID, 
#                      db: Session = Depends(get_db),
#                      current_user: UserCreate = Depends(user_utils.get_current_user)):
#     return script_utils.get_script_notes_by_script_id(db=db, script_id=script_id)

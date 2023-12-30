##### Fastapi Imports

from fastapi import APIRouter, Depends, HTTPException

##### Database Models & SQLAlchemy Imports
from sqlalchemy.orm import Session
from db_models.db_setup import get_db
from datetime import datetime
import uuid

# from . import crud_scripts, database, schemas, auth

##### Pydantic Imports
from pydantic_schemas.script_pydantic_models import Script, ScriptCreate
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


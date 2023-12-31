
##### Fastapi Imports
from fastapi import APIRouter, Depends, HTTPException

##### Database Models & SQLAlchemy Imports
from db_models.db_setup import get_db
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

##### Pydantic Imports
from pydantic_schemas.script_version_pydantic_models import ScriptVersionCreate, ScriptVersion, ScriptVersionsListResponse
from pydantic_schemas.user_pydantic_models import UserCreate

##### Utils Imports
from .api_utils import script_version_utils
from .api_utils import user_utils

# from . import crud_script_versions, database, schemas, auth

router = APIRouter()

@router.post("/script-versions", tags=["Script Versions"], response_model=ScriptVersion, description= "Whenever a user presess ctrl+s or saves the script that is when we store the version of the script")
def create_script_version(
    script_details: ScriptVersionCreate,
    # Other version-related parameters here as needed
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    new_script_version = script_version_utils.create_script_version(
        db, script_details.script_id,
        script_details.content, 
        script_details.change_summary, script_details.modified_by
    )
    return new_script_version

@router.get("/script-versions/{version_id}", tags=["Script Versions"], response_model=ScriptVersion)
def read_script_version(
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    script_version = script_version_utils.get_script_version(db, version_id)
    if not script_version:
        raise HTTPException(status_code=404, detail="Script Version not found")
    return script_version

# @router.put("/script-versions/{version_id}", tags=["Script Versions"], response_model=ScriptVersion)
# def update_script_version(
#     version_id: uuid.UUID,
#     script_details: ScriptVersionCreate,
#     # Other version-related parameters here as needed
#     db: Session = Depends(get_db),
#     current_user: UserCreate = Depends(user_utils.get_current_user)
# ):
#     created_at = datetime.utcnow().isoformat()
#     updated_script_version = script_version_utils.update_script_version(
#         db, version_id, script_details.script_id, 
#         script_details.content, script_details.change_summary, 
#         script_details.modified_by
#     )
#     if not updated_script_version:
#         raise HTTPException(status_code=404, detail="Script Version not found")
#     return updated_script_version

@router.delete("/script-versions/{version_id}", tags=["Script Versions"])
def delete_script_version(
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    deleted = script_version_utils.delete_script_version(db, version_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Script version not found")
    return {"message": "Script version deleted successfully"}

@router.get("/scripts/{script_id}/versions", tags=["Script Versions"], response_model=ScriptVersionsListResponse)
def get_all_script_versions(
    script_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    script_versions = script_version_utils.get_all_script_versions(db, script_id)
    if not script_versions:
        raise HTTPException(status_code=404, detail="No versions found for this script")
    print(script_versions)
    return {"versions": list(script_versions)}

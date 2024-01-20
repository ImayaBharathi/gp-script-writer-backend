
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
from pydantic_schemas.generic_pydantic_models import CustomResponse

##### Utils Imports
from .api_utils import script_version_utils
from .api_utils import user_utils

# from . import crud_script_versions, database, schemas, auth

router = APIRouter()

@router.post("/script-versions", tags=["Script Versions"], response_model=CustomResponse, description= "Whenever a user presess ctrl+s or saves the script that is when we store the version of the script")
def create_script_version(
    script_details: ScriptVersionCreate,
    # Other version-related parameters here as needed
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    script_exist = script_version_utils.check_if_script_id_exist(db, script_details.script_id)
    if script_exist:
        new_script_version = script_version_utils.create_script_version(
            db, script_details.script_id,
            script_details.content, 
            script_details.change_summary, script_details.modified_by
        )
        new_script_version = vars(new_script_version)
        new_script_version.pop('_sa_instance_state')
        success = True
        message = "Script Version Created"
        return CustomResponse(success=success, message=message, data=[new_script_version])
        # return new_script_version
    else:
        return CustomResponse(success=False, message="Script ID does not exits, create your script first", data=[])

@router.get("/script-versions/{version_id}", tags=["Script Versions"], response_model=CustomResponse)
def read_script_version(
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    script_version = script_version_utils.get_script_version(db, version_id)
    if not script_version:
        return CustomResponse(success=False, message="Script version not found", data=[])
        # raise HTTPException(status_code=404, detail="Script Version not found")
    script_version = vars(script_version)
    script_version.pop('_sa_instance_state')
    success = True
    message = "Script Version fetched"
    return CustomResponse(success=success, message=message, data=[script_version])

    # return script_version

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

@router.delete("/script-versions/{version_id}", tags=["Script Versions"], response_model=CustomResponse)
def delete_script_version(
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    deleted = script_version_utils.delete_script_version(db, version_id)
    if not deleted:
        return CustomResponse(success=False, message="Script version not found", data=[])
        # raise HTTPException(status_code=404, detail="Script version not found")
    success = True
    message = "Script Version deleted"
    return CustomResponse(success=success, message=message, data=[])
    # return {"message": "Script version deleted successfully"}

@router.get("/scripts/{script_id}/versions", tags=["Script Versions"], response_model=CustomResponse)
def get_all_script_versions(
    script_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    script_versions = script_version_utils.get_all_script_versions(db, script_id)
    if not script_versions:
        return CustomResponse(success=False, message="No Script Versions not found", data=[])
        # raise HTTPException(status_code=404, detail="No versions found for this script")
    script_versions_ = []
    for scpt in script_versions:
        scpt_ = vars(scpt)
        scpt_.pop('_sa_instance_state')
        script_versions_.append(scpt_)
    success = True
    message = "Script Versions Fetched"
    return CustomResponse(success=success, message=message, data=script_versions_)
    # return {"versions": list(script_versions)}

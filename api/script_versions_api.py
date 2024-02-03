
##### Fastapi Imports
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect


##### Database Models & SQLAlchemy Imports
from db_models.db_setup import get_db
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

##### Pydantic Imports
from pydantic_schemas.script_version_pydantic_models import ScriptVersionCreate, ScriptVersion, ScriptDraftCreate
from pydantic_schemas.user_pydantic_models import UserCreate
from pydantic_schemas.generic_pydantic_models import CustomResponse

##### Utils Imports
from .api_utils import script_version_utils
from .api_utils import user_utils

# from . import crud_script_versions, database, schemas, auth
import json

router = APIRouter()

@router.post("/script-versions", tags=["Script Versions"], response_model=CustomResponse, description= "Whenever a user presess ctrl+s or saves the script that is when we store the version of the script")
def create_script_version(
    script_details: ScriptVersionCreate,
    # Other version-related parameters here as needed
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    script_exist = script_version_utils.check_if_script_id_exist(db, script_details.script_id, current_user.user_id)
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



################## DRAFT
################## DRAFT
################## DRAFT
@router.post("/script-drafts", tags=["Script Drafts"], response_model=CustomResponse)
def create_script_draft(
    script_details: ScriptDraftCreate,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    new_script_draft = script_version_utils.create_script_draft(
        db,
        script_details.script_id,
        script_details.content,
        current_user.user_id,
        script_details.remarks
    )
    new_script_draft = vars(new_script_draft)
    new_script_draft.pop('_sa_instance_state')
    success = True
    message = "Script Draft Created"
    return CustomResponse(success=success, message=message, data=[new_script_draft])

@router.get("/script-drafts/{draft_id}", tags=["Script Drafts"], response_model=CustomResponse)
def read_script_draft(
    draft_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    script_draft = script_version_utils.get_script_draft(db, draft_id)
    if not script_draft:
        return CustomResponse(success=False, message="Script draft not found", data=[])
    script_draft = vars(script_draft)
    script_draft.pop('_sa_instance_state')
    success = True
    message = "Script Draft fetched"
    return CustomResponse(success=success, message=message, data=[script_draft])

@router.put("/script-drafts/{draft_id}", tags=["Script Drafts"], response_model=CustomResponse)
def update_script_draft(
    draft_id: uuid.UUID,
    script_details: ScriptDraftCreate,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    updated_script_draft = script_version_utils.update_script_draft(
        db,
        draft_id,
        script_details.script_id,
        script_details.content,
        current_user.user_id,
        script_details.remarks
    )
    if not updated_script_draft:
        return CustomResponse(success="False", message="Draft Not found", data=[])
    updated_script_draft = vars(updated_script_draft)
    updated_script_draft.pop('_sa_instance_state')
    success = True
    message = "Script Draft updated"
    return CustomResponse(success=success, message=message, data=[updated_script_draft])

@router.delete("/script-drafts/{draft_id}", tags=["Script Drafts"], response_model=CustomResponse)
def delete_script_draft(
    draft_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    deleted = script_version_utils.delete_script_draft(db, draft_id)
    if not deleted:
        return CustomResponse(success=False, message="Script draft not found", data=[])
    success = True
    message = "Script Draft deleted"
    return CustomResponse(success=success, message=message, data=[])








# ----------------
## Capitalize Strings
@router.post("/upper_case/", tags=["Script Versions"], response_model=CustomResponse)
def make_data_uppercase(caps_string: str, 
                       db: Session = Depends(get_db),
                       current_user: UserCreate = Depends(user_utils.get_current_user)):
    success = True
    message = "Upper Case applied"
    return CustomResponse(success=success, message=message, data=[{"capped_string": caps_string.upper()}])

@router.websocket("/ws_upper_case/")
async def websocket_upper_case(
    websocket: WebSocket,
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    try:
        while True:
            data = await websocket.receive_text()

            capped_string = data.upper()
            
            # Create a CustomResponse object
            custom_response = CustomResponse(success=True, message="Upper Case applied", data=[{"capped_string": capped_string}])
            
            # Convert CustomResponse to JSON string
            json_response = json.dumps(custom_response.dict())
            
            # Send JSON response through WebSocket
            await websocket.send_text(json_response)

    except WebSocketDisconnect:
        # Handle exceptions and send custom error response
        error_response = CustomResponse(success=False, message="Internal Server Error", data=[])
        json_error_response = json.dumps(error_response.model_dump())
        await websocket.send_text(json_error_response)


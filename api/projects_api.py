##### Fastapi Imports

from fastapi import APIRouter, Depends, HTTPException

##### Database Models & SQLAlchemy Imports
from sqlalchemy.orm import Session
from db_models.db_setup import get_db
from datetime import datetime
import uuid
from typing import List

##### Pydantic Imports
# from pydantic_schemas.script_pydantic_models import Script, ScriptCreate, ScriptNote, ScriptNoteCreate
from pydantic_schemas.user_pydantic_models import UserCreate
from pydantic_schemas.generic_pydantic_models import CustomResponse

##### Utils Imports
from .api_utils import script_utils
from .api_utils import user_utils
from .api_utils import project_utils

from loguru import logger

router = APIRouter()

@router.put("/projects/{project_id}", tags=["Projects"], response_model=CustomResponse)
def update_project_name(
    project_id: uuid.UUID,
    project_name: str,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    project = project_utils.get_project(db, project_id)
    
    if not project:
        return  CustomResponse(success=False, message="Project not found", data=[])
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = project_utils.update_project_name(db, project_id, project_name)
    project = vars(project)
    project.pop('_sa_instance_state')

    success = True
    message = "Project name updated successfully"
    return CustomResponse(success=success, message=message, data=[project])


@router.delete("/projects/{project_id}", tags=["Projects"], response_model=CustomResponse)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    project = project_utils.get_project(db, project_id)
    
    if not project:
        return  CustomResponse(success=False, message="Project not found", data=[])
        # raise HTTPException(status_code=404, detail="Project not found")
    
    project_utils.delete_project(db, project_id)

    success = True
    message = "Project deleted successfully"
    return CustomResponse(success=success, message=message, data=[])

@router.get("/projects", tags=["Projects"], response_model=CustomResponse)
def list_projects_with_scripts(
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    projects = project_utils.get_projects_with_scripts(db, current_user.user_id)

    if not projects:
        return  CustomResponse(success=False, message="No projects found", data=[])
        # raise HTTPException(status_code=404, detail="No projects found")


    success = True
    message = "Projects retrieved successfully"
    return CustomResponse(success=success, message=message, data=projects)
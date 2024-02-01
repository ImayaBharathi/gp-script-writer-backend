from sqlalchemy.orm import Session
from db_models.models import scripts_db_models, projects_db_models
from pydantic_schemas.script_pydantic_models import ScriptNoteCreate, ScriptNote
from typing import List
import uuid


def get_latest_project(db: Session, user_id: str) -> projects_db_models.Projects:
    latest_project = db.query(projects_db_models.Projects).filter(projects_db_models.Projects.user_id == user_id).order_by(projects_db_models.Projects.created_at.desc()).first()
    return latest_project
def create_project(db: Session, user_id: str) -> projects_db_models.Projects:
    latest_project = get_latest_project(db, user_id)

    if latest_project:
        # Extract the counter from the project name
        counter = int(latest_project.project_name.split()[-1])

        # Increment the counter for the new project
        new_project_name = f"Untitled Project {counter + 1}"
    else:
        # If no previous projects, start with counter 1
        new_project_name = "Untitled Project 1"

    new_project = projects_db_models.Projects(user_id=user_id, project_name=new_project_name)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


def create_project_script(db: Session, project_id: str, script_id: str) -> projects_db_models.ProjectScripts:
    new_project_script = projects_db_models.ProjectScripts(project_id=project_id, script_id=script_id)
    db.add(new_project_script)
    db.commit()
    db.refresh(new_project_script)
    return new_project_script


def get_project(db: Session, project_id: uuid.UUID) -> projects_db_models.Projects:
    return db.query(projects_db_models.Projects).filter(projects_db_models.Projects.project_id == project_id).first()

def update_project_name(db: Session, project_id: uuid.UUID, project_name: str) -> projects_db_models.Projects:
    project = db.query(projects_db_models.Projects).filter(projects_db_models.Projects.project_id == project_id).first()
    if project:
        project.project_name = project_name
        db.commit()
        db.refresh(project)
    return project

def get_projects_with_scripts(db: Session, user_id: uuid.UUID):
    projects = db.query(projects_db_models.Projects).filter(projects_db_models.Projects.user_id == user_id).all()

    response_data = []
    for project in projects:
        print(project)
        project_data = vars(project)
        project_data.pop("_sa_instance_state")

        script_ids = [ps.script_id for ps in db.query(projects_db_models.ProjectScripts).filter(projects_db_models.ProjectScripts.project_id == project.project_id).all()]
        scripts = db.query(scripts_db_models.Script).filter(scripts_db_models.Script.script_id.in_(script_ids)).all()
        scripts_data_list = []
        for script in scripts:
            scripts_data = vars(script)
            scripts_data.pop("_sa_instance_state")
            scripts_data_list.append(scripts_data)
        project_data["scripts"] = scripts_data_list
        response_data.append(project_data)
    print(response_data)
    return response_data


def delete_project(db: Session, project_id: uuid.UUID):
    project = db.query(projects_db_models.Projects).filter(projects_db_models.Projects.project_id == project_id).first()
    
    if project:
        # Get associated script_ids
        script_ids = [ps.script_id for ps in db.query(projects_db_models.ProjectScripts).filter(projects_db_models.ProjectScripts.project_id == project_id).all()]

        # Delete associated ProjectScripts
        db.query(projects_db_models.ProjectScripts).filter(projects_db_models.ProjectScripts.project_id == project_id).delete()

        # Delete associated scripts
        db.query(scripts_db_models.Script).filter(scripts_db_models.Script.script_id.in_(script_ids)).delete(synchronize_session=False)
        
        # Delete project
        db.delete(project)
        db.commit()

from sqlalchemy.orm import Session
from db_models.models import scripts_db_models
from pydantic_schemas.script_pydantic_models import ScriptNoteCreate, ScriptNote
from typing import List
import uuid

def create_script(
    db: Session,
    title: str,
    genre: str,
    user_id: int,
    logline: str,
    last_modified_at: str,
    # Other script-related metadata parameters here as needed
):
    new_script = scripts_db_models.Script(
        title=title,
        genre=genre,
        user_id=user_id,
        logline = logline
        # Other script-related metadata assignments here
    )

    db.add(new_script)
    db.commit()
    db.refresh(new_script)
    return new_script

def get_script(db: Session, script_id: int):
    return db.query(scripts_db_models.Script).filter(scripts_db_models.Script.script_id == script_id).first()

def get_all_script(db: Session):
    return db.query(scripts_db_models.Script).all()

def update_script(
    db: Session,
    script_id: int,
    title: str,
    genre: str,
    user_id: int,
    logline: str,
    last_modified_at: str,
    # Other script-related metadata parameters here as needed
):
    script = db.query(scripts_db_models.Script).filter(scripts_db_models.Script.script_id == script_id).first()
    if script:
        script.title = title
        script.genre = genre
        script.user_id = user_id
        script.logline = logline
        # script.last_modified_at = last_modified_at ### testing the onupdate=datetime.utcnow from sqlalchemy
        # Update other script-related metadata as needed
        db.commit()
        db.refresh(script)
        return script

def delete_script(db: Session, script_id: int):
    script = db.query(scripts_db_models.Script).filter(scripts_db_models.Script.script_id == script_id).first()
    if script:
        db.delete(script)
        db.commit()
        return True
    return False



def create_script_note(db: Session, script_note: ScriptNoteCreate):
    db_script_note = scripts_db_models.ScriptNotes(**script_note.model_dump())
    db.add(db_script_note)
    db.commit()
    db.refresh(db_script_note)
    return db_script_note

# Get all ScriptNotes for a Script
def get_script_notes_by_script_id(db: Session, script_id: int):
    return db.query(scripts_db_models.ScriptNotes).filter(scripts_db_models.ScriptNotes.script_id == script_id).all()

# Get ScriptNote by ID
def get_script_note_by_id(db: Session, note_id: int):
    return db.query(scripts_db_models.ScriptNotes).filter(scripts_db_models.ScriptNotes.note_id == note_id).first()

# Update ScriptNote
def update_script_note(db: Session, db_note: scripts_db_models.ScriptNotes, note_content: str):
    db_note.note_content = note_content
    db.commit()
    db.refresh(db_note)
    return db_note

# Delete ScriptNote
def delete_script_note(db: Session, db_note: scripts_db_models.ScriptNotes):
    db.delete(db_note)
    db.commit()
    return {"message": "ScriptNote deleted successfully"}

# Get all ScriptNotes for a Script
def get_script_notes_by_script_id(db: Session, script_id: str) -> List[scripts_db_models.ScriptNotes]:
    return db.query(scripts_db_models.ScriptNotes).filter(scripts_db_models.ScriptNotes.script_id == script_id).all()

from sqlalchemy.orm import Session
from db_models.models import scripts_db_models
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

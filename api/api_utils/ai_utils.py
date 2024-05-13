
from sqlalchemy.orm import Session
from db_models.models import scripts_db_models

from typing import List
import uuid, os, json
from loguru import logger



def create_script_to_ai_mapping_table(db: Session, script_id: uuid.UUID, taskingai_chat_id: str, other_info:dict ):
    available_mapping = db.query(scripts_db_models.ScriptAIMapping).filter(scripts_db_models.ScriptAIMapping.script_id == script_id).first()
    if available_mapping:
        return False,available_mapping
    
    new_ai_mapping = scripts_db_models.ScriptAIMapping(
        script_id=script_id,
        taskingai_chat_id=taskingai_chat_id,
        info_column=json.dumps(other_info)
    )
    db.add(new_ai_mapping)
    db.commit()
    db.refresh(new_ai_mapping)
    return True, new_ai_mapping




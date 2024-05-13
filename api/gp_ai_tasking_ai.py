import os

##### Fastapi Imports
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, FastAPI

##### Azure imports
from azure.storage.blob import BlobClient

##### Database Models & SQLAlchemy Imports
from sqlalchemy.orm import Session
from db_models.db_setup import get_db
from datetime import datetime
import uuid
from typing import List, Optional

##### Pydantic Imports
from pydantic_schemas.script_pydantic_models import Script, ScriptCreate, ScriptNote, ScriptNoteCreate, ScriptSubmission
from pydantic_schemas.user_pydantic_models import UserCreate
from pydantic_schemas.generic_pydantic_models import CustomResponse

##### Utils Imports
from .api_utils import script_utils
from .api_utils import user_utils
from .api_utils import project_utils
from .api_utils import ai_utils

##### Logging
from loguru import logger
import traceback

##### Langchain Models
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel,Field

##### Tasking AI Imports
import taskingai
from taskingai.assistant import Assistant
from taskingai.assistant.chat import Chat
from taskingai.assistant.memory import AssistantNaiveMemory
from taskingai.assistant.message import Message


router = APIRouter()

heading_description_json = {
    "Initial Scene": "The opening moment of the story, setting the tone, time, place, and introducing the main character or characters.",
    "Theme Introduction": "Introduce the central theme or message of the story, setting the stage for thematic exploration.",
    "Background Setup": "Provide background information about the characters, setting, and context necessary for understanding the story.",
    "Inciting Incident": "The event that disrupts the status quo and sets the main plot in motion, forcing the protagonist to take action.",
    "Decision Point": "A critical moment where the protagonist must make a choice that will drive the rest of the story.",
    "Act Two Transition": "The point where the story moves from the setup to the main conflict, often marked by a significant event or decision.",
    "Secondary Plotline": "Introduce a subplot that complements or contrasts with the main plot, adding depth to the story.",
    "Central Story Development": "The main plot unfolds, with the protagonist facing challenges and obstacles as they pursue their goal.",
    "Pivotal Moment": "A key event or revelation that significantly impacts the protagonist or the plot, leading to a shift in direction.",
    "Rising Tensions": "Tension and stakes increase as the protagonist faces escalating challenges and obstacles.",
    "Low Point": "The protagonist faces their darkest moment, feeling defeated or hopeless.",
    "Crisis Moment": "The final, most intense confrontation or challenge that the protagonist must overcome.",
    "Final Act Entry": "The beginning of the resolution, where the protagonist prepares for the climax and the story's conclusion.",
    "Climax": "The most intense and pivotal moment of the story, where the main conflict is resolved.",
    "Closing Scene": "The resolution of the story, tying up loose ends and providing closure for the characters and the audience."
}

class BeatSheetHeadingDescription(BaseModel):
    initial_scene: str = Field(description=heading_description_json["Initial Scene"])
    theme_introduction: str = Field(description=heading_description_json["Theme Introduction"])
    background_setup: str = Field(description=heading_description_json["Background Setup"])
    inciting_incident: str = Field(description=heading_description_json["Inciting Incident"])
    decision_point: str = Field(description=heading_description_json["Decision Point"])
    act_two_transition: str = Field(description=heading_description_json["Act Two Transition"])
    secondary_plotline: str = Field(description=heading_description_json["Secondary Plotline"])
    central_story_development: str = Field(description=heading_description_json["Central Story Development"])
    pivotal_moment: str = Field(description=heading_description_json["Pivotal Moment"])
    rising_tensions: str = Field(description=heading_description_json["Rising Tensions"])
    low_point: str = Field(description=heading_description_json["Low Point"])
    crisis_moment: str = Field(description=heading_description_json["Crisis Moment"])
    final_act_entry: str = Field(description=heading_description_json["Final Act Entry"])
    climax: str = Field(description=heading_description_json["Climax"])
    closing_scene: str = Field(description=heading_description_json["Closing Scene"])

parser = JsonOutputParser(pydantic_object=BeatSheetHeadingDescription)
TASKING_API_KEY = os.getenv("TASKING_API_KEY")
logger.info(TASKING_API_KEY)
taskingai.init(api_key=TASKING_API_KEY)
beat_sheet_assistant_id = "X5lMCt5jRtMXs9jeDwQLIcqr"

@router.post("/generate_beat_sheet", tags=["AI"], response_model=CustomResponse, summary="Generate beat sheet")
def generating_beat_sheet_from_ai(
    scripts: ScriptCreate,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user)
):
    try:

        beat_sheet_assistant : Assistant = taskingai.assistant.get_assistant(
            assistant_id=beat_sheet_assistant_id
        )

        new_project = project_utils.create_project(db, user_id=current_user.user_id)
        new_script = script_utils.create_script(db, scripts.title, scripts.genre, current_user.user_id, scripts.logline, last_modified_at="")
        _ = project_utils.create_project_script(db, project_id=new_project.project_id, script_id=new_script.script_id)

        chat: Chat = taskingai.assistant.create_chat(
            assistant_id=beat_sheet_assistant_id,
            name=f'{str(new_script.script_id)}',
            metadata={
                "user_id": f"{current_user.user_id}",
                "script_title": f"{new_script.title}",
                "others": "we can think of something else as well",
            }
        )
        logger.info(chat)
        user_input  = """
        title: <title_placeholder>

        genre: <genre_placeholder>

        logline: <logline_placeholder>
        
        format instructions: <format_instruction_placeholder>
        """
        user_input = user_input.replace("<title_placeholder>", scripts.title)
        user_input = user_input.replace("<genre_placeholder>", scripts.genre)
        user_input = user_input.replace("<logline_placeholder>", scripts.logline)
        user_input = user_input.replace("<format_instruction_placeholder>", parser.get_format_instructions())
        user_message = taskingai.assistant.create_message(
        assistant_id=beat_sheet_assistant.assistant_id,
        chat_id=chat.chat_id,
        text=user_input,
        )
        logger.info(chat.chat_id)
        assistant_message: Message = taskingai.assistant.generate_message(
        assistant_id=beat_sheet_assistant.assistant_id,
        chat_id=chat.chat_id
        )
        logger.info(f"{assistant_message.content.text}")
        beat_sheet_json  = parser.parse(assistant_message.content.text)
        data_for_db= {"parsed_ai_response": beat_sheet_json, "tasking_message_info": assistant_message.model_dump_json(), "tasking_chat_info": chat.model_dump_json(), "project_information": str(new_project.project_id), "user_message": user_message.model_dump_json() }

        check, update_ai_mapping = ai_utils.create_script_to_ai_mapping_table(db, script_id=new_script.script_id, taskingai_chat_id=chat.chat_id, other_info=data_for_db)

        # new_script = vars(new_script)
        # new_script.pop('_sa_instance_state')
        if not check:
            logger.error("AI mapping already available for a new script")
            logger.error(f"{new_script}")
        success = True
        message = "Beat sheet generated successfully"
        logger.info(f"{new_script.__dict__}")
        data = [beat_sheet_json]
        return CustomResponse(success=success, message=message, data=data)
    
    except Exception as e:
        logger.error("Exception occurred while generating beat sheet from AI")
        logger.error(e)
        logger.error("-----------")
        logger.error(traceback.format_exc())
        success = False
        message = "Server Side Exception"
        return CustomResponse(success=success, message=message, data=[])
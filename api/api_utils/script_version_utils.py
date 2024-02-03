import uuid
import difflib
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from db_models.models import scripts_db_models
from azure.storage.blob import BlobServiceClient, ContentSettings

connection_string = "DefaultEndpointsProtocol=https;AccountName=gpuicomponents;AccountKey=PrW5sG4NaCAHl6N4XUVX04uPxAbcGyEjDSVbs8HJlYLDmk+jG0f6LmQ/64tLMwKHcov0Dd/NdYlW+AStGDOoaw==;EndpointSuffix=core.windows.net"

### the below doesnt check if the script belong to ths user if present
# def check_if_script_id_exist(db: Session,script_id: uuid.UUID):
#     return db.query(scripts_db_models.Script).filter(scripts_db_models.Script.script_id == script_id).all()

def check_if_script_id_exist(db: Session, script_id: uuid.UUID, user_id: uuid.UUID):
    return db.query(scripts_db_models.Script).filter(
        (scripts_db_models.Script.script_id == script_id) & 
        (scripts_db_models.Script.user_id == user_id)
    ).first()

def check_if_script_draft_id_exist(db: Session, script_id: uuid.UUID, user_id: uuid.UUID, draft_id: uuid.UUID):
    return db.query(scripts_db_models.ScriptDraftsFromVersion).filter(
        (scripts_db_models.ScriptDraftsFromVersion.script_id == script_id) & 
        (scripts_db_models.ScriptDraftsFromVersion.user_id == user_id) & 
        (scripts_db_models.ScriptDraftsFromVersion.draft_id == draft_id)
    ).first()

def create_script_version(
    db: Session,
    script_id: uuid.UUID,
    content: str,
    change_summary: str,
    modified_by: uuid.UUID,
    # Other version-related metadata parameters here as needed
):

    existing_script_version = db.query(scripts_db_models.ScriptVersion).filter(
        scripts_db_models.ScriptVersion.script_id == script_id
    ).first()
    if existing_script_version:

        # If there's a latest version, compute the diff
        diff = difflib.unified_diff(
            existing_script_version.content.splitlines(),
            content.splitlines(),
            lineterm=''
        )
        if not list(diff):
            logger.info("script content has no change, so skipping version creating")
            return existing_script_version
        else:
            # Update the existing script version
            existing_script_version.content = content
            existing_script_version.change_summary = change_summary
            existing_script_version.modified_by = modified_by
            # Update other version-related metadata as needed
            db.commit()
            db.refresh(existing_script_version)
            return existing_script_version
    else:
        # Create a new script version
        new_script_version = scripts_db_models.ScriptVersion(
            script_id=script_id,
            content=content,
            script_file_url="temporary_url",
            change_summary=change_summary,
            modified_by=modified_by
            # Other version-related metadata assignments here
        )
        db.add(new_script_version)
        db.commit()
        db.refresh(new_script_version)
        return new_script_version

def get_script_version(db: Session, version_id: uuid.UUID):
    return db.query(scripts_db_models.ScriptVersion).filter(scripts_db_models.ScriptVersion.version_id == version_id).first()

# def update_script_version(
#     db: Session,
#     version_id: uuid.UUID,
#     script_id: uuid.UUID,
#     content: str,
#     script_file_url: str,
#     change_summary: str,
#     modified_by: uuid.UUID
#     # Other version-related metadata parameters here as needed
# ):
#     script_version = db.query(scripts_db_models.ScriptVersion).filter(scripts_db_models.ScriptVersion.version_id == version_id).first()
#     if script_version:
#         script_version.script_id = script_id
#         script_version.content = content
#         script_version.script_file_url = script_file_url
#         script_version.change_summary = change_summary
#         script_version.modified_by = modified_by
#         # Update other version-related metadata as needed
#         db.commit()
#         db.refresh(script_version)
#         return script_version
#     else:
#         return None

def delete_script_version(db: Session, version_id: uuid.UUID):
    script_version = db.query(scripts_db_models.ScriptVersion).filter(scripts_db_models.ScriptVersion.version_id == version_id).first()

    if script_version:
        db.delete(script_version)
        db.commit()
        return True
    return False

def get_all_script_versions(db: Session, script_id: uuid.UUID):
    return (db.query(scripts_db_models.ScriptVersion)
            .filter(scripts_db_models.ScriptVersion.script_id == script_id)
            .order_by(asc(scripts_db_models.ScriptVersion.created_at)) 
            .limit(10)
            .all())

def upload_script_content_to_blob_storage(connection_string, content, version_id_for_blob_name,container_name="scripts-versions", content_type="text/plain"):
    try:
        # Create a BlobServiceClient using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # a unique name for the blob using version UUID
        blob_name = str(version_id_for_blob_name)+".txt"

        # Get a client to interact with a specific container
        container_client = blob_service_client.get_container_client(container_name)

        # Create a blob client to upload content
        blob_client = container_client.get_blob_client(blob_name)

        # Upload content to the blob
        blob_client.upload_blob(content, content_settings=ContentSettings(content_type=content_type), overwrite=True)

        # Return the URL of the uploaded blob for reference
        return blob_client.url
    except Exception as e:
        # Handle exceptions or errors during upload
        print(f"An error occurred: {e}")
        return None


# Functions for Script Drafts

def create_script_draft(
    db: Session,
    script_id: uuid.UUID,
    content: str,
    user_id: uuid.UUID,
    remarks: str
):
    new_script_draft = scripts_db_models.ScriptDraftsFromVersion(
        script_id=script_id,
        content=content,
        user_id=user_id,
        remarks=remarks
    )
    db.add(new_script_draft)
    db.commit()
    url = upload_script_content_to_blob_storage(connection_string,content, new_script_draft.draft_id)
    new_script_draft.script_file_url = url
    db.commit()
    db.refresh(new_script_draft)
    return new_script_draft

def get_script_draft(db: Session, draft_id: uuid.UUID):
    return db.query(scripts_db_models.ScriptDraftsFromVersion).filter(scripts_db_models.ScriptDraftsFromVersion.draft_id == draft_id).first()

def update_script_draft(
    db: Session,
    draft_id: uuid.UUID,
    script_id: uuid.UUID,
    content: str,
    user_id: uuid.UUID,
    remarks: str
):
    updated_script_draft = db.query(scripts_db_models.ScriptDraftsFromVersion).filter(
                (scripts_db_models.ScriptDraftsFromVersion.script_id == script_id) & 
                (scripts_db_models.ScriptDraftsFromVersion.user_id == user_id) & 
                (scripts_db_models.ScriptDraftsFromVersion.draft_id == draft_id)
                ).first()
    
    if updated_script_draft:
        url = upload_script_content_to_blob_storage(connection_string,content, updated_script_draft.draft_id)
        updated_script_draft.script_id = script_id
        updated_script_draft.content = content
        updated_script_draft.user_id = user_id
        updated_script_draft.script_file_url = url
        updated_script_draft.remarks = remarks
        db.commit()
        db.refresh(updated_script_draft)
        return updated_script_draft
    else:
        return None

def delete_script_draft(db: Session, draft_id: uuid.UUID):
    deleted_draft = db.query(scripts_db_models.ScriptDraftsFromVersion).filter(scripts_db_models.ScriptDraftsFromVersion.draft_id == draft_id).first()
    if deleted_draft:
        db.delete(deleted_draft)
        db.commit()
        return True
    return False


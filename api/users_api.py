import json
##### Fastapi Imports

from fastapi import APIRouter,Depends, FastAPI, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

##### Pydantic Imports
from pydantic_schemas.user_pydantic_models import UserCreate, Token, UserDetails
from pydantic_schemas.generic_pydantic_models import CustomResponse

##### Database Models & SQLAlchemy Imports
from db_models.models import users_db_models
from db_models.db_setup import get_db
from sqlalchemy.orm import Session

##### Utils Imports
from .api_utils import user_utils

##### Logging
from loguru import logger
# from logging_module import log_to_azure_storage

import uuid

##### Other Imports
# from google.auth.transport import requests
# from google.oauth2 import id_token


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register/", tags=["Users"], response_model=CustomResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # log_to_azure_storage(user.email, "User Created", True)
        tokens_or_message = user_utils.create_user(db, user)
        if "access_token" in tokens_or_message and "refresh_token" in tokens_or_message:
            success = True
            message = "User Created"
            logger.info(tokens_or_message)
            return CustomResponse(success=success, message=message, data=[tokens_or_message])
            # return JSONResponse(content=tokens_or_message, status_code=201)  # User created, return tokens
        else:
            return CustomResponse(success=False, message="User Already Exists", data=[])
            # return JSONResponse(content=tokens_or_message, status_code=400)  # User already exists
    except Exception as e:
        return CustomResponse(success=False, message="Server Side Exception", data=[])
        # raise HTTPException(status_code=500, detail=str(e))
    
# @router.post("/token/", tags=["Users"], response_model=CustomResponse)
# def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = user_utils.authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         return CustomResponse(success=False, message="Incorrect email or password", data=[])
#         # raise HTTPException(status_code=400, detail="Incorrect email or password")
#     data = user_utils.create_tokens_for_user(user)
#     success = True
#     message = "Login Success"
#     return CustomResponse(success=success, message=message, data=[data])

@router.post("/token/", tags=["Users"], response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # return CustomResponse(success=False, message="Incorrect email or password", data=[])
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    data = user_utils.create_tokens_for_user(user)
    success = True
    message = "Login Success"
    return data
    # return CustomResponse(success=success, message=message, data=[data])

@router.post("/token-login/", tags=["Users"], response_model=CustomResponse)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return CustomResponse(success=False, message="Incorrect email or password", data=[])
        # raise HTTPException(status_code=400, detail="Incorrect email or password")
    data = user_utils.create_tokens_for_user(user)
    success = True
    message = "Login Success"
    # return data
    return CustomResponse(success=success, message=message, data=[data])

@router.post("/refresh-token", tags=["Users"], response_model=CustomResponse)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    tokens = user_utils.refresh_access_token(db,refresh_token)
    if tokens:
        success = True
        message = "Generated Access token from refresh token"
        return CustomResponse(success=success, message=message, data=[tokens])
    else:
        return CustomResponse(success=False, message="Incorrect refresh token", data=[])

@router.get("/user/me", tags=["Users"])
def get_user_id_based_on_access_token(
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    return current_user.user_id

@router.post("/user-details", tags=["User Details"], response_model=CustomResponse)
def create_user_details(
    other_info: dict,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    other_info = json.dumps(other_info)
    logger.info("other_info")
    response = user_utils.create_user_details(db, current_user.user_id, other_info)
    logger.info("created")
    response.other_info = json.loads(response.other_info)
    logger.info("updated")
    response = vars(response)
    data = {}
    data['other_info'] = response['other_info'] 
    data['user_details_id'] = response['user_details_id']
    data['updated_at'] = response['updated_at']
    data['user_id'] = response['user_id']
    data['created_at']= response['created_at']
    success = True
    message = "User details created"
    return CustomResponse(success=success, message=message, data=[data])

@router.get("/user-details", tags=["User Details"], response_model=CustomResponse)
def read_user_details(
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    logger.info(current_user.user_id)
    user_details = user_utils.get_user_details(db, current_user.user_id)
    logger.info(user_details)
    if not user_details:
        return CustomResponse(success=False, message="UserDetails not found", data=[])
        # raise HTTPException(status_code=404, detail="UserDetails not found")
    user_details.other_info  = json.loads(user_details.other_info)
    user_details = vars(user_details)
    data = {}
    data['other_info'] = user_details['other_info'] 
    data['user_details_id'] = user_details['user_details_id']
    data['updated_at'] = user_details['updated_at']
    data['user_id'] = user_details['user_id']
    data['created_at']= user_details['created_at']
    success = True
    message = "User details fetched"
    return CustomResponse(success=success, message=message, data=[data])
    # return user_details

@router.put("/user-details/{user_details_id}", tags=["User Details"], response_model=CustomResponse)
def update_user_details(
    user_details_id: uuid.UUID,
    other_info: dict,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    other_info = json.dumps(other_info)
    user_details = user_utils.update_user_details(db, user_details_id, other_info)
    if not user_details:
        return CustomResponse(success=False, message="UserDetails not found", data=[])
        # raise HTTPException(status_code=404, detail="UserDetails not found")
    user_details.other_info = json.loads(user_details.other_info)
    user_details = vars(user_details)
    data = {}
    data['other_info'] = user_details['other_info'] 
    data['user_details_id'] = user_details['user_details_id']
    data['updated_at'] = user_details['updated_at']
    data['user_id'] = user_details['user_id']
    data['created_at']= user_details['created_at']
    success = True
    message = "User details updated"
    return CustomResponse(success=success, message=message, data=[data])
    # return user_details

@router.delete("/user-details/{user_details_id}", tags=["User Details"], response_model=CustomResponse)
def delete_user_details(
    user_details_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    deleted = user_utils.delete_user_details(db, user_details_id)
    if not deleted:
        return CustomResponse(success=False, message="UserDetails not found", data=[])
        # raise HTTPException(status_code=404, detail="UserDetails not found")
    success = True
    message = "User details deleted successfully"
    return CustomResponse(success=success, message=message, data=[])
    # return {"message": "UserDetails deleted successfully"}

######## For SSO Logins

@router.get("/auth/google/login", tags=["Users"], response_model=CustomResponse)
async def google_login():
    # Redirect the user to Google's OAuth page to initiate the login process
    redirect_url = user_utils.get_google_login_url()
    success = True
    message = "URL generated successfully"
    return CustomResponse(success=success, message=message, data=[redirect_url])
    # return {"url": redirect_url}

@router.get("/auth/google/callback", tags=["Users"], response_model=CustomResponse)
async def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        # Exchange the received authorization code for user information
        google_user_info = user_utils.exchange_code_for_user_info(code)
        logger.info(google_user_info)
        # log_to_azure_storage.info("")

        # Process the user information and store/update in the database
        user = user_utils.get_or_create_user(db, google_user_info)
        logger.info(user)
        # Generate access token and refresh token for the user
        tokens = user_utils.create_tokens_for_user(user)
        success = True
        message = "Login Success"
        return CustomResponse(success=success, message=message, data=[tokens])
        # return tokens
    
    except Exception as e:
        return CustomResponse(success=False, message="Login Failed - Server Side Issue", data=[])
        # Handle exceptions appropriately
        # raise HTTPException(status_code=500, detail=str(e))


######## Things to write
# 1) Forgot Password #### needs azure cloud to send emails for 
# 2) Reset Password  #### needs azure cloud to send emails for 
    
@router.post("/logout", tags=["Users"], response_model=CustomResponse)
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), 
                 current_user: UserCreate = Depends(user_utils.get_current_user)):
    if user_utils.revoke_token(db, token, current_user.user_id):
        return CustomResponse(success=True, message="Logout successful", data=[])
    else:
        return CustomResponse(success=False, message="Invalid token or token already revoked", data=[])

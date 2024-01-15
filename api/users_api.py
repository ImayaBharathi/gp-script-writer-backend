import json
##### Fastapi Imports

from fastapi import APIRouter,Depends, FastAPI, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

##### Pydantic Imports
from pydantic_schemas.user_pydantic_models import UserCreate, Token, UserDetails

##### Database Models & SQLAlchemy Imports
from db_models.models import users_db_models
from db_models.db_setup import get_db
from sqlalchemy.orm import Session

##### Utils Imports
from .api_utils import user_utils

##### Logging
from loguru import logger

##### Other Imports
# from google.auth.transport import requests
# from google.oauth2 import id_token


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register/", tags=["Users"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        tokens_or_message = user_utils.create_user(db, user)
        if "access_token" in tokens_or_message and "refresh_token" in tokens_or_message:
            return JSONResponse(content=tokens_or_message, status_code=201)  # User created, return tokens
        else:
            return JSONResponse(content=tokens_or_message, status_code=400)  # User already exists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/token/", tags=["Users"], response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return user_utils.create_tokens_for_user(user)

@router.post("/refresh-token", tags=["Users"], response_model=Token)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    tokens = user_utils.refresh_access_token(db,refresh_token)
    return tokens

@router.post("/user-details", tags=["User Details"], response_model=UserDetails)
def create_user_details(
    other_info: dict,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    logger.info(other_info)
    other_info = json.dumps(other_info)
    response = user_utils.create_user_details(db, current_user.user_id, other_info)
    logger.info("------")
    logger.info(response)
    response.other_info = json.loads(response.other_info)
    return response

@router.get("/user/me", tags=["Users"])
def get_user_id_based_on_access_token(
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    return current_user.user_id


@router.get("/user-details", tags=["User Details"], response_model=UserDetails)
def read_user_details(
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    logger.info(current_user.user_id)
    user_details = user_utils.get_user_details(db, current_user.user_id)
    logger.info(user_details)
    if not user_details:
        raise HTTPException(status_code=404, detail="UserDetails not found")
    user_details.other_info  = json.loads(user_details.other_info)
    return user_details

@router.put("/user-details/{user_details_id}", tags=["User Details"], response_model=UserDetails)
def update_user_details(
    user_details_id: int,
    other_info: dict,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    user_details = user_utils.update_user_details(db, user_details_id, other_info)
    if not user_details:
        raise HTTPException(status_code=404, detail="UserDetails not found")
    return user_details

@router.delete("/user-details/{user_details_id}", tags=["User Details"])
def delete_user_details(
    user_details_id: int,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    deleted = user_utils.delete_user_details(db, user_details_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="UserDetails not found")
    return {"message": "UserDetails deleted successfully"}

######## For SSO Logins

@router.get("/auth/google/login", tags=["Users"])
async def google_login():
    # Redirect the user to Google's OAuth page to initiate the login process
    redirect_url = user_utils.get_google_login_url()
    return {"url": redirect_url}

@router.get("/auth/google/callback", tags=["Users"], response_model=Token)
async def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        # Exchange the received authorization code for user information
        google_user_info = user_utils.exchange_code_for_user_info(code)

        # Process the user information and store/update in the database
        user = user_utils.get_or_create_user(db, google_user_info)

        # Generate access token and refresh token for the user
        tokens = user_utils.create_tokens_for_user(user)
        
        return tokens
    
    except Exception as e:
        # Handle exceptions appropriately
        raise HTTPException(status_code=500, detail=str(e))


######## Things to write
# 1) Forgot Password #### needs azure cloud to send emails for 
# 2) Reset Password  #### needs azure cloud to send emails for 
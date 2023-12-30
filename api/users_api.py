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

@router.post("/google-login", tags=["Users"], response_model=Token)
def google_login(id_token: str):
    try:
        return {
            "access_token": "working on it",
            "refresh_token": "working on it",
            "token_type": "bearer"
        }
        # # Verify Google ID token
        # client_id = "your-google-client-id"  # Replace with your Google Client ID
        # idinfo = id_token.verify_oauth2_token(id_token, requests.Request(), client_id)

        # # Extract user information from the verified token
        # email = idinfo['email']
        # # Check if user with this email exists in your system, if not create one

        # # Generate access and refresh tokens for the user
        # access_token = user_utils.create_access_token(data={"sub": email}, expires_delta=30)  # Implement this function
        # refresh_token = user_utils.create_access_token(data={"sub": email}, expires_delta=30)  # Implement this function

        # return {
        #     "access_token": access_token,
        #     "refresh_token": refresh_token,
        #     "token_type": "bearer"
        # }
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google ID token")
    

@router.post("/user-details", tags=["User Details"], response_model=UserDetails)
def create_user_details(
    user_id: int,
    other_info: str,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    return user_utils.create_user_details(db, user_id, other_info)

@router.get("/user-details/{user_details_id}", tags=["User Details"], response_model=UserDetails)
def read_user_details(
    user_details_id: int,
    db: Session = Depends(get_db),
    current_user: UserCreate = Depends(user_utils.get_current_user),
):
    user_details = user_utils.get_user_details(db, user_details_id)
    if not user_details:
        raise HTTPException(status_code=404, detail="UserDetails not found")
    return user_details

@router.put("/user-details/{user_details_id}", tags=["User Details"], response_model=UserDetails)
def update_user_details(
    user_details_id: int,
    other_info: str,
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

######## Things to write
# 1) Forgot Password #### needs azure cloud to send emails for 
# 2) Reset Password  #### needs azure cloud to send emails for 




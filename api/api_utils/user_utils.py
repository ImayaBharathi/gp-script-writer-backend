from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from db_models.models import users_db_models
from db_models.db_setup import get_db
from pydantic_schemas.user_pydantic_models import UserCreate

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import requests
import json
import uuid
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

import requests


# from google.auth.transport import requests
# from google.oauth2 import id_token

from fastapi import Depends, HTTPException
from typing import Optional
from loguru import logger
# from logging_module import log_to_azure_storage


SECRET_KEY = "c3e9b330d915e0c04d8fa1cb2168366b9f078aa463388b998b3d1cf3a55b1d1e10"  # Replace with a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1300
REFRESH_TOKEN_EXPIRE_DAYS = 7



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(db: Session, user: UserCreate):
    username = user.email.split("@")[0]  # Derive username from email
    hashed_password = get_password_hash(user.password)
    # Check if user with the same email exists
    try:
        existing_user = db.query(users_db_models.User).filter(users_db_models.User.email == user.email).first()
        print(existing_user)
        if existing_user:
            return {"message": "User with this email already exists"}
        else:
            pass
    except NoResultFound:
        pass
    
    try:
        db_user = users_db_models.User(username=username, email=user.email, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        access_token = create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
        refresh_token = create_access_token(data={"sub": db_user.email}, expires_delta=refresh_token_expires)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except IntegrityError:
        db.rollback()
        return {"message": "Error creating user"}


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(users_db_models.User).filter(users_db_models.User.email == username).first()
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_tokens_for_user(user: users_db_models.User):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token = create_access_token(data={"sub": user.email}, expires_delta=refresh_token_expires)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[users_db_models.User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check if token is blacklisted
    blacklisted_token = db.query(users_db_models.BlacklistedToken).filter(users_db_models.BlacklistedToken.token == token).first()
    if blacklisted_token:
        raise HTTPException(status_code=401, detail="Token is from logged out user, Retry logging in again")

    user = db.query(users_db_models.User).filter(users_db_models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def verify_refresh_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except JWTError:
        return False

def get_email_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_from_email(db: Session,email: str) -> users_db_models.User:
    return db.query(users_db_models.User).filter(users_db_models.User.email == email).first()

def refresh_access_token(db:Session,refresh_token: str) -> str:
    if not verify_refresh_token(refresh_token):
        return False
        # raise HTTPException(status_code=401, detail="Invalid refresh token")

    email = get_email_from_token(refresh_token)
    # Assuming you have the user's email, fetch user from the database
    user = get_user_from_email(db,email)  # Implement your logic to get user from email
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(data={"sub": user.email}, expires_delta=refresh_token_expires)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


GOOGLE_CLIENT_ID = "997620213023-iup3a0pbqe5a6brf968ejpu6rr8g3l19.apps.googleusercontent.com"  # Replace with your Google Client ID
GOOGLE_CLIENT_SECRET = "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"  # Replace with a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# def verify_google_id_token(id_token: str):
#     try:
#         idinfo = id_token.verify_oauth2_token(id_token, requests.Request(), GOOGLE_CLIENT_ID)
#         return idinfo.get("email")
#     except ValueError:
#         return None
    
def get_user_id_from_email(email: str, db: Session) -> int:
    user = db.query(users_db_models.User).filter(users_db_models.User.email == email).first()
    return user.user_id if user else None



def create_user_details(db: Session, user_id: int, other_info: str):
    existing_user_details = db.query(users_db_models.UserDetails).filter(users_db_models.UserDetails.user_id == user_id).first()
    if existing_user_details:
        # If a record already exists for the user_id, update it instead of creating a new one
        existing_user_details.other_info = other_info
        db.commit()
        db.refresh(existing_user_details)
        return existing_user_details
    else:
        # Create a new record
        new_user_details = users_db_models.UserDetails(user_id=user_id, other_info=other_info)
        db.add(new_user_details)
        db.commit()
        db.refresh(new_user_details)
        return new_user_details


def get_user_details(db: Session, user_id: int):
    return db.query(users_db_models.UserDetails).filter(users_db_models.UserDetails.user_id == user_id).first()

def update_user_details(db: Session, user_details_id: int, other_info: str):
    user_details = db.query(users_db_models.UserDetails).filter(users_db_models.UserDetails.user_details_id == user_details_id).first()
    if user_details:
        json_val = json.loads(user_details.other_info)
        json_val.update(json.loads(other_info))
        user_details.other_info = json.dumps(json_val)
        db.commit()
        db.refresh(user_details)
        return user_details

def delete_user_details(db: Session, user_details_id: int):
    user_details = db.query(users_db_models.UserDetails).filter(users_db_models.UserDetails.user_details_id == user_details_id).first()
    if user_details:
        db.delete(user_details)
        db.commit()
        return True
    return False


def get_google_login_url():
    # Construct the URL for redirecting users to Google's OAuth page
    scope = "openid email profile https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/contacts"  # Define necessary scopes based on your requirements
    # redirect_uri = "http://localhost:8000/auth/google/callback"  # Your callback URL
    redirect_uri = "http://gp-backend.eastus.azurecontainer.io:8000/auth/google/callback"
    auth_endpoint = "https://accounts.google.com/o/oauth2/auth"

    params = {
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "access_type": "offline",
        "prompt": "consent"  # Force consent screen for new permissions
    }

    url = f"{auth_endpoint}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return url

def get_user_email(access_token):
    r = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            params={'access_token': access_token})
    return r.json()

def exchange_code_for_user_info(code):
    # Exchange the received authorization code for user information
    token_endpoint = "https://oauth2.googleapis.com/token"

    payload = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": "http://localhost:8000/auth/google/callback",
        "grant_type": "authorization_code"
    }

    response = requests.post(token_endpoint, data=payload)
    if response.status_code == 200:
        user_info = response.json()
        logger.info(user_info.get("id_token", "false"))
        
        # Decode the ID token using the public keys for verification
        user_details = get_user_email(user_info.get("access_token", "false"))
        user_info["name"] = user_details.get("name", "")
        user_info["email"] = user_details.get("email","")
        user_info["other_user_details"] = user_details
        # logger.info(user_info)
        return user_info
    else:
        raise Exception("Failed to exchange code for user info")
    
def get_or_create_user(db: Session, google_user_info: dict):
    # Check if the user already exists based on the Google ID
    logger.info(google_user_info['id_token'])
    # existing_google_user = db.query(users_db_models.GoogleAuth).filter_by(google_unique_id_for_user=google_user_info['id_token']).first()
    existing_google_user = db.query(users_db_models.User).filter_by(email=google_user_info['email']).first()
    
    if existing_google_user:
        # User already exists, return the associated user
        return existing_google_user
    
    # User doesn't exist, create a new user
    new_user = users_db_models.User(
        username=google_user_info.get('name', 'Google User'),
        email=google_user_info.get('email', 'example@example.com')
    )
    db.add(new_user)
    db.commit()
    
    # Create GoogleAuth entry for the user
    new_google_user = users_db_models.GoogleAuth(
        google_unique_id_for_user=google_user_info['id_token'],
        user_id=new_user.user_id,
        other_google_data = json.dumps(google_user_info)
    )
    db.add(new_google_user)
    db.commit()
    return new_user

def revoke_token(db: Session, token: str, user_id: uuid.UUID) -> bool:
    try:
        blacklisted_token = users_db_models.BlacklistedToken(token=token, user_id=user_id)
        db.add(blacklisted_token)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False

def get_email_by_token(db: Session, token: str):
    # Dummy implementation, replace with actual token validation and user retrieval
    user = db.query(users_db_models.User).filter(users_db_models.User.access_token == token).first()
    return user.email if user else None

def extract_username(email: str):
    return email.split('@')[0]

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# from google.auth.transport import requests
# from google.oauth2 import id_token

from fastapi import Depends, HTTPException
from typing import Optional


SECRET_KEY = "c3e9b330d915e0c04d8fa1cb2168366b9f078aa463388b998b3d1cf3a55b1d1e10"  # Replace with a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
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
        raise HTTPException(status_code=401, detail="Invalid refresh token")

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


GOOGLE_CLIENT_ID = "your-google-client-id"  # Replace with your Google Client ID
SECRET_KEY = "your-secret-key"  # Replace with a secure secret key
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


def get_user_details(db: Session, user_details_id: int):
    return db.query(users_db_models.UserDetails).filter(users_db_models.UserDetails.user_details_id == user_details_id).first()

def update_user_details(db: Session, user_details_id: int, other_info: str):
    user_details = db.query(users_db_models.UserDetails).filter(users_db_models.UserDetails.user_details_id == user_details_id).first()
    if user_details:
        user_details.other_info = other_info
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
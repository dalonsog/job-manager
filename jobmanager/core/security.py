import os
import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlmodel import Session
from jobmanager.models.dbmodels import User


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    data_to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta    
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

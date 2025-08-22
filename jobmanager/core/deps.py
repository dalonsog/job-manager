from typing import Annotated, Generator
from sqlmodel import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from jobmanager.core.db import engine
from jobmanager.core.security import get_token_payload
from jobmanager.models.dbmodels import User
from jobmanager.models.user import Role
from jobmanager.models.token import Token, TokenData
from jobmanager.crud.user import get_user_by_email


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_session() -> Generator:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[Token, Depends(oauth_scheme)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data: TokenData = get_token_payload(token)
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user_by_email(session=session, user_email=token_data.username)
    if not user:
        raise credentials_exception
    
    return user


def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    return user


def get_current_active_user_admin(
    user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    if not user.role == Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough privileges"
        )
    return user


def get_current_active_user_admin_or_maintainer(
    user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    if not (user.role == Role.ADMIN or user.role == Role.MAINTAINER):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough privileges"
        )
    return user

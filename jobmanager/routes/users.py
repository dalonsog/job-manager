import uuid
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends, Body, Query
from jobmanager.models.dbmodels import User
from jobmanager.crud.user import (
    get_users,
    get_user_by_id,
    get_user_by_email,
    create_user
)
from jobmanager.crud.account import get_account_by_id
from jobmanager.models.user import (
    UserCreate,
    UserPublic,
    Role
)
from jobmanager.core.deps import (
    SessionDep,
    get_current_active_user,
    get_current_active_user_admin_or_maintainer
)


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserPublic])
def read_users(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
):
    if current_user.role == Role.ADMIN:
        return get_users(session=session, offset=skip, limit=limit)
    else:
        return get_users(
            session=session,
            offset=skip,
            limit=limit,
            account_id=current_user.account_id
        )


@router.get("/{user_id}", response_model=UserPublic)
def read_user(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    user = get_user_by_id(session=session, user_id=user_id)

    if not user \
            or (current_user.role != Role.ADMIN \
                    and current_user.account_id != user.account_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    return user


@router.post("/", response_model=UserPublic)
def create_new_user(
    session: SessionDep,
    user: Annotated[UserCreate, Body()],
    current_user: Annotated[User, Depends(
        get_current_active_user_admin_or_maintainer
    )],
    account_id_in: Annotated[uuid.UUID | None, Query()] = None
):
    user_db = get_user_by_email(session=session, name=user.email)
    if user_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {user.email} already exists"
        )
    
    account_id = current_user.account_id
    if current_user.role == Role.ADMIN and account_id_in:
        account_id = account_id_in
        account_db = get_account_by_id(session=session, account_id=account_id)
        if not account_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_id} not found"
            )
    
    user_in = UserCreate(
        email=user.email,
        password=user.password,
        role=user.role
    )
    created_user = create_user(
        session=session,
        user=user_in,
        account_id=account_id
    )
    return created_user

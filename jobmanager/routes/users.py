import uuid
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body, Query
from jobmanager.models.dbmodels import User
from jobmanager.crud.account import get_account_by_id
from jobmanager.crud.user import (
    get_users,
    get_user_by_id,
    get_user_by_email,
    create_user,
    remove_user,
    update_user
)
from jobmanager.models.message import Message
from jobmanager.models.user import (
    UserCreate,
    UserPublic,
    Role
)
from jobmanager.core.deps import (
    SessionDep,
    ActiveUserDep,
    ActiveAdminMaintainerDep
)


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserPublic])
def read_users(
    session: SessionDep,
    current_user: ActiveUserDep,
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
    current_user: ActiveUserDep
):
    user = get_user_by_id(session=session, user_id=user_id)

    if not user or (current_user.role != Role.ADMIN \
                    and current_user.account_id != user.account_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    return user


@router.post(
    "/",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED
)
def create_new_user(
    session: SessionDep,
    user: Annotated[UserCreate, Body()],
    current_user: ActiveAdminMaintainerDep,
    account_id: Annotated[uuid.UUID | None, Query()] = None
):
    user_db = get_user_by_email(session=session, user_email=user.email)
    if user_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {user.email} already exists"
        )
    
    account_id_in = current_user.account_id
    if current_user.role == Role.ADMIN:
        if account_id:
            account_id_in = account_id
        
        account_db = get_account_by_id(
            session=session,
            account_id=account_id_in
        )
        if not account_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_id_in} not found"
            )
        
        if account_db.is_global and user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only admins can be assigned to that account"
            )
        
        if not account_db.is_global and user.role == Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Admins must be assigned to a global account"
            )
        
    if current_user.role == Role.MAINTAINER and user.role == Role.ADMIN:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Not allowed to create new admins"
            )
    
    user_in = UserCreate(
        email=user.email,
        password=user.password,
        role=user.role
    )
    created_user = create_user(
        session=session,
        user=user_in,
        account_id=account_id_in
    )
    return created_user


@router.put("/{user_id}/deactivate", response_model=Message)
def deactivate_user(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: ActiveAdminMaintainerDep
):
    user = get_user_by_id(session=session, user_id=user_id)
    if not user or (current_user.role == Role.MAINTAINER \
                    and current_user.account_id != user.account_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} is already deactivated"
        )
    
    user_data = user.model_dump()
    user_data['is_active'] = False
    user_in = User(**user_data)
    updated_user = update_user(
        session=session,
        user=user,
        user_in=user_in
    )

    return Message(message=f"User {updated_user.id} successfully deactivated")


@router.put("/{user_id}/activate", response_model=Message)
def activate_user(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: ActiveAdminMaintainerDep
):
    user = get_user_by_id(session=session, user_id=user_id)
    if not user or (current_user.role == Role.MAINTAINER \
                    and current_user.account_id != user.account_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} is already active"
        )
    
    user_data = user.model_dump()
    user_data['is_active'] = True
    user_in = User(**user_data)
    updated_user = update_user(
        session=session,
        user=user,
        user_in=user_in
    )

    return Message(message=f"User {updated_user.id} successfully activated")


@router.delete("/{user_id}", response_model=Message)
def delete_user(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: ActiveAdminMaintainerDep
):
    user = get_user_by_id(session=session, user_id=user_id)
    if not user or (current_user.role == Role.MAINTAINER \
                    and user.account_id != current_user.account_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    remove_user(session=session, user=user)
    
    return Message(message=f"User {user_id} removed")

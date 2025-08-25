import uuid
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends, Body, Query
from jobmanager.models.dbmodels import User
from jobmanager.crud.user import (
    get_users,
    get_user_by_id,
    get_user_by_email,
    create_user,
    remove_user,
    update_user
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


@router.put("/{user_id}/deactivate", response_model=UserPublic)
def deactivate_user(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(
        get_current_active_user_admin_or_maintainer
    )]
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
    print(user_data)
    user_in = User(**user_data)
    updated_user = update_user(
        session=session,
        user=user,
        user_in=user_in
    )

    return updated_user


@router.put("/{user_id}/activate", response_model=UserPublic)
def activate_user(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(
        get_current_active_user_admin_or_maintainer
    )]
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
    user_data['is_active'] = False
    user_in = User(**user_data)
    updated_user = update_user(
        session=session,
        user=user,
        user_in=user_in
    )

    return updated_user


@router.delete("/{user_id}")
def delete_account(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(
        get_current_active_user_admin_or_maintainer
    )]
):
    user = get_user_by_id(session=session, user_id=user_id)
    if not user or (current_user.role == Role.MAINTAINER \
                    and user.account_id != current_user.account_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    remove_user(session=session, user=user)
    
    return {"message": f"User {user_id} removed"}

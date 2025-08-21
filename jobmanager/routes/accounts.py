import uuid
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body
from jobmanager.models.dbmodels import Account
from jobmanager.models.account import AccountRegister, AccountCreate, AccountPublic
from jobmanager.core.deps import SessionDep
from jobmanager.crud.account import (
    create_account,
    get_accounts,
    get_account_by_id,
    get_account_by_name,
    remove_account,
    update_account
)


router = APIRouter(prefix="/accounts", tags=["account"])


@router.get("/", response_model=list[AccountPublic])
def read_accounts(session: SessionDep, skip: int = 0, limit: int = 100):
    return get_accounts(session=session, offset=skip, limit=limit)


@router.get("/{account_id}", response_model=AccountPublic)
def read_accounts(session: SessionDep, account_id: uuid.UUID):
    account = get_account_by_id(session=session, account_id=account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    
    # check whether the account is global and current user is admin
    # only admins should be able to see global accounts
    
    return account


@router.post("/", response_model=AccountPublic)
def create_new_account(
    session: SessionDep,
    account: Annotated[AccountRegister, Body()]
):
    account_db = get_account_by_name(session=session, name=account.name)
    if account_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Account {account.name} already exists"
        )
    
    # check whether the new account is global and current user is admin
    # only admins should be able to create global accounts
    account_in = AccountCreate(name=account.name)
    created_account = create_account(session=session, account=account_in)
    return created_account


@router.put("/{account_id}/deactivate", response_model=AccountPublic)
def deactivate_account(
    session: SessionDep,
    account_id: uuid.UUID,
):
    # check whether current user is admin
    # only admins should be able to deactivate accounts
    account = get_account_by_id(session=session, account_id=account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    
    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account {account_id} is already deactivated"
        )
    
    account_data = account.model_dump()
    account_data['is_active'] = False
    account_in = AccountCreate(**account_data)
    updated_account = update_account(
        session=session,
        account=account,
        account_in=account_in
    )

    return updated_account


@router.put("/{account_id}/activate", response_model=AccountPublic)
def activate_account(
    session: SessionDep,
    account_id: uuid.UUID,
):
    # check whether current user is admin
    # only admins should be able to deactivate accounts
    account = get_account_by_id(session=session, account_id=account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    
    if account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account {account_id} is already active"
        )
    
    account_data = account.model_dump()
    account_data['is_active'] = True
    account_in = AccountCreate(**account_data)
    updated_account = update_account(
        session=session,
        account=account,
        account_in=account_in
    )

    return updated_account


@router.delete("/{account_id}")
def read_accounts(session: SessionDep, account_id: uuid.UUID):
    # check whether current user is admin or maintainer
    # only admins and maintainers should be able to remove accounts
    
    account = get_account_by_id(session=session, account_id=account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    
    # check whether current user is maintainer of account
    # accounts should only be removed by their maintainers
    
    # check whether the account is global and current user is admin
    # only admins should be able to remove global accounts

    remove_account(session=session, account=account)
    
    return {"message": f"Account {account_id} removed"}

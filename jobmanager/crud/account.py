import uuid
from sqlmodel import Session, select
from jobmanager.models.dbmodels import Account
from jobmanager.models.account import AccountCreate


def create_account(session: Session, account: AccountCreate) -> Account:
    account_db = Account.model_validate(account)
    session.add(account_db)
    session.commit()
    session.refresh(account_db)
    return account_db


def get_accounts(session: Session, offset: int, limit: int) -> list[Account]:
    statement = select(Account).offset(offset).limit(limit)
    accounts = session.exec(statement).all()
    return accounts


def get_account_by_id(session: Session, account_id: uuid.UUID) -> Account:
    account = session.get(Account, account_id)
    return account


def get_account_by_name(session: Session, name: str) -> Account:
    statement = select(Account).where(Account.name == name)
    account = session.exec(statement).first()
    return account


def remove_account(session: Session, account: Account) -> None:
    session.delete(account)
    session.commit()


def update_account(
    session: Session,
    account: Account,
    account_in: AccountCreate
) -> Account:
    account_data = account_in.model_dump(exclude_unset=True)
    extra_data = {}
    account.sqlmodel_update(account_data, update=extra_data)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

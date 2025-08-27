from sqlmodel import Session
from jobmanager.crud.user import authenticate_user
from jobmanager.core.security import create_access_token


def get_user_data(
    session: Session,
    email: str,
    password: str
) -> dict[str, any]: 
    user = authenticate_user(
        session=session,
        user_email=email,
        user_pwd=password
    )
    return {
        "token": create_access_token(data={"sub": user.email}),
        "data": user
    }

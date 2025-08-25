import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jobmanager.models.token import Token, TokenData
from jobmanager.core.config import settings


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
    encoded_jwt = jwt.encode(
        data_to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_token_payload(token: Token) -> TokenData:
    try:
        payload: dict = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=settings.ALGORITHM
        )
        username = payload.get("sub")
        if not username:
            raise InvalidTokenError
        return TokenData(username=username)
    except InvalidTokenError:
        raise

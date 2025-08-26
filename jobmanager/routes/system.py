from fastapi import APIRouter
from jobmanager.models.message import Message
from jobmanager.core.config import VERSION


router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health-check", response_model=bool)
def health_check():
    return True


@router.get("/version", response_model=Message)
def get_version():
    return Message(message=VERSION)

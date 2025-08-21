from fastapi import APIRouter
from jobmanager.models.dbmodels import User
from jobmanager.models.user import UserBase, UserCreate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])

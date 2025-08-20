from fastapi import APIRouter
from jobmanager.models.all import User, UserBase, UserCreate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])

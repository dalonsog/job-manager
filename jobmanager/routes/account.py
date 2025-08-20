from fastapi import APIRouter
from jobmanager.models.all import Account, AccountBase, \
    AccountCreate, AccountPublic

router = APIRouter(prefix="/account", tags=["account"])

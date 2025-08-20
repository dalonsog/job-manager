from fastapi import APIRouter
from jobmanager.models.all import Job, JobBase, JobCreate, JobPublic

router = APIRouter(prefix="/jobs", tags=["jobs"])

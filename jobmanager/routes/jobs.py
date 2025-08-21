from fastapi import APIRouter
from jobmanager.models.dbmodels import Job
from jobmanager.models.job import JobBase, JobCreate, JobPublic

router = APIRouter(prefix="/jobs", tags=["jobs"])

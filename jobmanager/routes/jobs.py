import uuid
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body, Query, Depends
from jobmanager.models.dbmodels import Job
from jobmanager.models.job import JobCreate, JobPublic, Status
from jobmanager.models.user import Role
from jobmanager.models.message import Message
from jobmanager.core.deps import (
    SessionDep,
    ActiveUserDep,
    get_current_active_user_admin
)
from jobmanager.crud.user import get_all_users, get_user_by_id
from jobmanager.crud.job import (
    get_all_jobs,
    get_job_by_id,
    create_job,
    remove_job,
    update_job
)


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobPublic])
def read_jobs(
    session: SessionDep,
    current_user: ActiveUserDep,
    skip: int = 0,
    limit: int = 100,
    status: Status | None = None
):
    users_in_account = get_all_users(
        session=session,
        account_id=current_user.account_id
    )
    users_id_list = [u.id for u in users_in_account]
    jobs = get_all_jobs(
        session=session,
        offset=skip,
        limit=limit,
        owner_id=users_id_list,
        status=status
    )
    return jobs


@router.get("/own", response_model=list[JobPublic])
def read_own_jobs(
    session: SessionDep,
    current_user: ActiveUserDep,
    skip: int = 0,
    limit: int = 100,
    status: Status | None = None
):
    jobs = get_all_jobs(
        session=session,
        offset=skip,
        limit=limit,
        owner_id=[current_user.id],
        status=status
    )
    return jobs


@router.get(
    "/all",
    dependencies=[Depends(get_current_active_user_admin)],
    response_model=list[JobPublic]
)
def read_all_jobs(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    status: Status | None = None
):
    jobs = get_all_jobs(
        session=session,
        offset=skip,
        limit=limit,
        status=status
    )
    return jobs


@router.get("/{job_id}", response_model=JobPublic)
def read_job(
    session: SessionDep,
    current_user: ActiveUserDep,
    job_id: uuid.UUID
):
    job = get_job_by_id(session=session, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    if job.owner_id != current_user.id:
        owner = get_user_by_id(session=session, user_id=job.owner_id)
        if owner.account_id != current_user.account_id \
                and current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found in account"
            )
        
    return job


@router.post("/", response_model=JobPublic, status_code=status.HTTP_201_CREATED)
def create_new_job(
    session: SessionDep,
    current_user: ActiveUserDep,
    job: Annotated[JobCreate, Body()],
    run_on_create: Annotated[bool | None, Query()] = False
):
    job_in = JobCreate(name=job.name, command=job.command)
    default_status = Status.RUNNING if run_on_create else Status.STOPPED
    created_job = create_job(
        session=session,
        job=job_in,
        owner_id=current_user.id,
        status=default_status
    )
    return created_job


@router.put("/{job_id}/stop", response_model=Message)
def stop_job(
    session: SessionDep,
    job_id: uuid.UUID,
    current_user: ActiveUserDep
):
    job = get_job_by_id(session=session, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    if job.owner_id != current_user.id:
        owner = get_user_by_id(session=session, user_id=job.owner_id)
        if owner.account_id != current_user.account_id \
                and current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found in account"
            )
        
        if current_user.role == Role.DEVELOPER:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Not authorized to stop job {job_id}"
            )
        
    if job.status == Status.STOPPED:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job {job_id} is already stopped"
            )
    
    job_data = job.model_dump()
    job_data['status'] = Status.STOPPED
    job_in = Job(**job_data)
    updated_job = update_job(
        session=session,
        job=job,
        job_in=job_in
    )

    return Message(message=f"Job {updated_job.id} successfully stopped")


@router.put("/{job_id}/run", response_model=Message)
def run_job(
    session: SessionDep,
    job_id: uuid.UUID,
    current_user: ActiveUserDep
):
    job = get_job_by_id(session=session, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    if job.owner_id != current_user.id:
        owner = get_user_by_id(session=session, user_id=job.owner_id)
        if owner.account_id != current_user.account_id \
                and current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found in account"
            )
        
        if current_user.role == Role.DEVELOPER:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Not authorized to stop job {job_id}"
            )
        
    if job.status == Status.RUNNING:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job {job_id} is already running"
            )
    
    job_data = job.model_dump()
    job_data['status'] = Status.RUNNING
    job_in = Job(**job_data)
    updated_job = update_job(
        session=session,
        job=job,
        job_in=job_in
    )

    return Message(message=f"Job {updated_job.id} successfully running")


@router.delete("/{job_id}", response_model=Message)
def delete_job(
    session: SessionDep,
    current_user: ActiveUserDep,
    job_id: uuid.UUID
):
    job = get_job_by_id(session=session, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    if job.owner_id != current_user.id:
        owner = get_user_by_id(session=session, user_id=job.owner_id)
        if owner.account_id != current_user.account_id \
                and current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found in account"
            )
        
        if current_user.role == Role.DEVELOPER:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Not authorized to delete job {job_id}"
            )
        
    remove_job(session=session, job=job)

    return Message(message=f"Job {job_id} removed")

import uuid
from sqlmodel import Session, select, col
from jobmanager.models.dbmodels import Job
from jobmanager.models.job import JobCreate, Status


def get_job_by_id(session: Session, job_id: uuid.UUID) -> Job:
    job = session.get(Job, job_id)
    return job


def get_all_jobs(
    session: Session,
    offset: int,
    limit: int,
    owner_id: list[uuid.UUID] | None = None
) -> list[Job]:
    if owner_id and len(owner_id):
        pre_statement = select(Job).where(col(Job.owner_id).in_(owner_id))
    else:
        pre_statement = select(Job)
    statement = pre_statement.offset(offset).limit(limit)
    jobs = session.exec(statement).all()
    return jobs


def create_job(
    session: Session,
    job: JobCreate,
    owner_id: uuid.UUID,
    status: Status = Status.STOPPED
) -> Job:
    job_db = Job.model_validate(
        job,
        update={
            "status": status,
            "owner_id": owner_id
        }
    )
    session.add(job_db)
    session.commit()
    session.refresh(job_db)
    return job_db


def remove_job(session: Session, job: Job) -> None:
    session.delete(job)
    session.commit()


def update_job(session: Session, job: Job, job_in: Job) -> Job:
    job_data = job_in.model_dump(exclude_unset=True)
    extra_data = {}
    job.sqlmodel_update(job_data, update=extra_data)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job

from fastapi import FastAPI
from jobmanager.routes import account, jobs, users
from jobmanager.core.db import create_db_and_tables

app = FastAPI()
app.include_router(account.router)
app.include_router(users.router)
app.include_router(jobs.router)


@app.get("/")
def root():
    return {"message": "Hello world"}


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

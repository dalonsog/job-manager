from fastapi import FastAPI
from jobmanager.routes import accounts, jobs, users, auth, system
from jobmanager.core.db import init_db


app = FastAPI()
app.include_router(accounts.router)
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(auth.router)
app.include_router(system.router)


@app.get("/")
def root():
    return {"message": "Hello world"}


# Only for development purposes. Remove on production
@app.on_event("startup")
def on_startup():
    init_db()

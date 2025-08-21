from dotenv import load_dotenv
from fastapi import FastAPI
from jobmanager.routes import accounts, jobs, users, auth
from jobmanager.core.db import init_db

# Only for development purposes. Remove on production
load_dotenv()

app = FastAPI()
app.include_router(accounts.router)
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Hello world"}


# Only for development purposes. Remove on production
@app.on_event("startup")
def on_startup():
    init_db()

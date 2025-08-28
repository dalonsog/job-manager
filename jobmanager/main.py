from fastapi import FastAPI
from jobmanager.routes import accounts, jobs, users, auth, system


app = FastAPI()
app.include_router(accounts.router)
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(auth.router)
app.include_router(system.router)


@app.get("/")
def root():
    return {"message": "Hello world"}

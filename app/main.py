from app.models import StateFlag
import asyncio
from contextlib import asynccontextmanager
from contextlib import suppress

import app.store as store
from app.scheduler import invoice_scheduler

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.store import get_job
from app.uploads import create_uploaded_job
from grpc_service.grpc_server import start_grpc_server


@asynccontextmanager
async def lifespan(_app: FastAPI):
    grpc_server = await start_grpc_server()
    scheduler_task = asyncio.create_task(
        invoice_scheduler(
            store.jobs,
            request_interval=30
        )
    )

    try:
        yield
    finally:
        scheduler_task.cancel()
        with suppress(asyncio.CancelledError):
            await scheduler_task
        await grpc_server.stop(grace=1)


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Invoice Processing API"}


@app.post("/jobs")
async def create_job_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    try:
        job = create_uploaded_job(file.filename or "", content)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "req_no": job.req_no,
        "state": job.state.value
    }


@app.get("/jobs/{req_no}/result")
def get_job_result(req_no: str):
    job = get_job(req_no)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job {req_no} not found"
        )

    if job.state == StateFlag.WAIT_RATE:
        return {
            "req_no": job.req_no,
            "state": job.state.value,
            "message": "Job is waiting"
        }

    if job.state == StateFlag.CALLING:
        return {
            "req_no": job.req_no,
            "state": job.state.value,
            "message": "Job is still processing"
        }

    if job.state == StateFlag.FAILED:
        return {
            "req_no": job.req_no,
            "state": job.state.value,
            "error": job.error
        }

    return {
        "req_no": job.req_no,
        "state": job.state.value,
        "result": job.result
    }

@app.get("/jobs/{req_no}/status")
def get_job_status(req_no: str):
    job = get_job(req_no)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job {req_no} not found"
        )

    return {
        "req_no": job.req_no,
        "state": job.state.value
    }

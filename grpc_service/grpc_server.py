"""gRPC adapter for the existing invoice pipeline."""
import json
import os

import grpc

from app import store
from app.models import StateFlag
from app.uploads import create_uploaded_job
from grpc_service import invoice_service_pb2 as pb
from grpc_service import invoice_service_pb2_grpc as rpc

# Allow PDFs up to approximately 20 MiB including protobuf overhead.
GRPC_OPTIONS = [("grpc.max_receive_message_length", 21 * 1024 * 1024)]



def job_response(job):
    return pb.JobResponse(req_no=job.req_no, state=job.state.value)


class InvoiceService(rpc.InvoiceServiceServicer):
    async def find_job(self, request, context):
        job = store.get_job(request.req_no)
        if job is None:
            await context.abort(grpc.StatusCode.NOT_FOUND, "Job not found")
        return job

    async def CreateJob(self, request, context):
        try:
            job = create_uploaded_job(request.filename, request.file_content)
        except ValueError as error:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))
        except OSError:
            await context.abort(grpc.StatusCode.INTERNAL, "Unable to save uploaded PDF")
        return job_response(job)

    async def GetJobStatus(self, request, context):
        return job_response(await self.find_job(request, context))

    async def GetJobResult(self, request, context):
        job = await self.find_job(request, context)
        return pb.JobResultResponse(
            req_no=job.req_no,
            state=job.state.value,
            result_json=json.dumps(job.result) if job.state == StateFlag.DONE else "",
            error=job.error or "",
        )

    async def ListJobs(self, request, context):
        return pb.JobListResponse(jobs=[job_response(job) for job in store.jobs.values()])

    async def DeleteJob(self, request, context):
        job = await self.find_job(request, context)
        if job.state == StateFlag.CALLING:
            await context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Job is processing")
        # Retain the uploaded PDF, as the existing REST pipeline does.
        del store.jobs[job.req_no]
        return pb.DeleteJobResponse(success=True)


async def start_grpc_server(address=None):
    server = grpc.aio.server(options=GRPC_OPTIONS)
    rpc.add_InvoiceServiceServicer_to_server(InvoiceService(), server)
    address = address or os.getenv("GRPC_ADDRESS", "127.0.0.1:50051")
    if not server.add_insecure_port(address):
        raise RuntimeError(f"Unable to bind gRPC server to {address}")
    await server.start()
    return server


if __name__ == "__main__":
    import uvicorn

    # One process, one store and one scheduler for both protocols.
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)

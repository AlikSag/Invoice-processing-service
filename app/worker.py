import asyncio

from app.models import StateFlag, Job
from app.azure_client import analyze_invoice, parse_invoice_result
from app.store import complete_job, fail_job

async def worker(job: Job, timeout: float=60):
    if job.state == StateFlag.CALLING:
        try:
            call_azure = await asyncio.wait_for(
                asyncio.to_thread(
                    analyze_invoice,
                    job.document_path
                    ),
                timeout=timeout,
            )
            parsed_result = parse_invoice_result(call_azure)
            job_result = complete_job(job.req_no, parsed_result)
        except asyncio.TimeoutError:
            job_result = fail_job(
                job.req_no,
                "Azure processing timeout"
            )
        except Exception as error:
            job_result = fail_job(job.req_no, str(error))

        return job_result
    else:
        raise ValueError("Job must be in CALLING state")

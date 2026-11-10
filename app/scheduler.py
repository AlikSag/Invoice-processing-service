import time
import asyncio

from app.models import StateFlag
from app.worker import worker
from app.store import update_state
import app.store as store

rate_limit_lock = asyncio.Lock()

async def invoice_scheduler(jobs, request_interval):
    while True:
        for job in jobs.values():

            if job.state == StateFlag.WAIT_RATE:

                async with rate_limit_lock:
                    now = time.time()

                    if (
                        job.state == StateFlag.WAIT_RATE
                        and now - store.last_azure_call_time >= request_interval
                    ):
                        updated_job = update_state(
                            job.req_no,
                            StateFlag.CALLING
                        )

                        store.last_azure_call_time = now

                    else:
                        updated_job = None

                if updated_job is not None:
                    asyncio.create_task(
                        worker(updated_job)
                    )
                    break

        remaining = request_interval - (
            time.time() - store.last_azure_call_time
        )

        if remaining > 0:
            await asyncio.sleep(remaining)
        else:
            await asyncio.sleep(1)

from app.models import Job, StateFlag

ALLOWED_TRANSITIONS = {
    StateFlag.WAIT_RATE : {StateFlag.CALLING},
    StateFlag.CALLING : {StateFlag.DONE, StateFlag.FAILED},
    StateFlag.DONE : set(),
    StateFlag.FAILED : set(),
}


jobs : dict[str, Job] = {}
last_azure_call_time : float = 0.00

def create_job(req_no : str, document_path :str):
    if req_no in jobs:
        raise ValueError(f"Job {req_no} already exists")

    job = Job(
        req_no = req_no,
        document_path = document_path,
        state = StateFlag.WAIT_RATE,
    )
    jobs[req_no] = job

    return job


def get_job(req_no : str):
    return jobs.get(req_no)


def update_state(req_no : str, new_state : StateFlag):
    job = get_job(req_no = req_no)

    if job is None:
        raise KeyError(f"Job{req_no} is not exist")
    if new_state not in ALLOWED_TRANSITIONS[job.state]:
        raise ValueError(
            f"Transition {job.state.value} -> {new_state.value} is not allowed"
        )
    job.state = new_state

    return job


def complete_job(req_no : str, result):
    job = get_job(req_no = req_no)

    if job is None:
        raise KeyError(f"Job{req_no} is not exist")

    update_state(req_no, StateFlag.DONE)
    job.result = result

    return job


def fail_job(req_no : str, error : str):
    job = get_job(req_no)

    if job is None:
        raise KeyError(f"Job{req_no} is not exist")

    update_state(req_no, StateFlag.FAILED)
    job.error = error

    return job

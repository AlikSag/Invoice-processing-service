import pytest

import app.store as store

from app.models import StateFlag
from app.store import (
    create_job,
    update_state,
    complete_job,
    fail_job,
)


def setup_function():
    store.jobs.clear()


def test_done_has_result():
    job = create_job("101", "invoice.pdf")
    update_state("101", StateFlag.CALLING)
    complete_job("101", {"total": 18.18})

    assert job.state == StateFlag.DONE
    assert job.result is not None
    assert job.error is None


def test_failed_has_error():
    job = create_job("102", "bad.pdf")
    update_state("102", StateFlag.CALLING)
    fail_job("102", "Azure error")

    assert job.state == StateFlag.FAILED
    assert job.error is not None
    assert job.result is None


def test_done_is_terminal():
    create_job("103", "invoice.pdf")
    update_state("103", StateFlag.CALLING)
    complete_job("103", {"total": 18.18})

    with pytest.raises(ValueError):
        update_state("103", StateFlag.CALLING)


def test_failed_is_terminal():
    create_job("104", "bad.pdf")
    update_state("104", StateFlag.CALLING)
    fail_job("104", "Azure error")

    with pytest.raises(ValueError):
        update_state("104", StateFlag.CALLING)


def test_req_no_is_unique():
    create_job("105", "invoice1.pdf")

    with pytest.raises(ValueError):
        create_job("105", "invoice2.pdf")

"""Shared upload handling for REST and gRPC."""
from pathlib import Path
from uuid import uuid4

from app.store import create_job

UPLOAD_DIR = Path("uploads")


def create_uploaded_job(filename: str, content: bytes):
    filename = Path(filename.replace("\\", "/")).name
    if not filename.lower().endswith(".pdf") or not content:
        raise ValueError("A filename ending in .pdf and non-empty PDF bytes are required")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    req_no = str(uuid4())
    file_path = UPLOAD_DIR / f"{req_no}_{filename}"
    file_path.write_bytes(content)
    return create_job(req_no=req_no, document_path=str(file_path))

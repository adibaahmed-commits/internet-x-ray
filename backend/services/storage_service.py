import os
import uuid
from pathlib import Path
from fastapi import UploadFile

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def save_upload_file(file: UploadFile) -> str:
    """
    Saves an UploadFile to /uploads with a unique filename.
    Returns the generated filename (not full path).
    """
    ext = Path(file.filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = UPLOAD_DIR / unique_name

    with open(dest_path, "wb") as buffer:
        buffer.write(file.file.read())

    return unique_name

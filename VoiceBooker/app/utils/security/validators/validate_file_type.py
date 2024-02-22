from typing import List

from fastapi import HTTPException

from app.utils.security.get_file_type import get_file_type


def validate_file_type(file: bytes, allowed_file_types: List[str]) -> str:
    file_type = get_file_type(file)

    if file_type not in allowed_file_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    return file_type

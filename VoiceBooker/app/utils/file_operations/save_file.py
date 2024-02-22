import uuid


def scramble_filename(filename: str) -> str:
    return f"{uuid.uuid4()}.{filename.split('.')[-1]}"


async def save_file(file, filename):
    with open(f"ebooks/{filename}", "wb") as buffer:
        buffer.write(await file.read())

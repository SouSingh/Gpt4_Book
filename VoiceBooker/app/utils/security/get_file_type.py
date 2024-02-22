import magic


def get_file_type(file: bytes) -> str:
    return magic.Magic(mime=True).from_buffer(file)

import os
from .storage_backends.local_backend import LocalStorage
from .storage_backends.s3_backend import S3Storage


def get_storage():
    backend = os.getenv("STORAGE_BACKEND", "local").lower()
    if backend == S3Storage.STORAGE_TYPE:
        return S3Storage(
            bucket=os.getenv("S3_BUCKET"),
            region=os.getenv("AWS_REGION"),
            key=os.getenv("AWS_ACCESS_KEY_ID"),
            secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
    elif backend == LocalStorage.STORAGE_TYPE:
        return LocalStorage(os.getenv("LOCAL_STORAGE_PATH", "/app/uploads"))
    else:
        raise Exception(f"Invalid storage backend provided. {backend}")

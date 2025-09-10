from fastapi.responses import FileResponse
import os
import boto3
import tempfile


class StorageBackend:
    STORAGE_TYPE: str

    def save(self, file, filename, app_name, version):
        raise NotImplementedError

    def get(self, path: str):
        raise NotImplementedError

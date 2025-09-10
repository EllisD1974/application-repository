from fastapi.responses import FileResponse
import os

from .base_backend import StorageBackend


class LocalStorage(StorageBackend):
    STORAGE_TYPE: str = "local"

    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def save(self, file, filename, app_name, version):
        app_dir = os.path.join(self.base_path, app_name, version)
        os.makedirs(app_dir, exist_ok=True)
        file_path = os.path.join(app_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file)
        return file_path

    def get(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} not found")
        return FileResponse(path, filename=os.path.basename(path))
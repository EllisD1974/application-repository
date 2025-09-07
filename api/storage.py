from fastapi.responses import FileResponse
import os
import boto3
import tempfile


class StorageBackend:
    def save(self, file, filename, app_name, version):
        raise NotImplementedError


class LocalStorage(StorageBackend):
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


class S3Storage(StorageBackend):
    def __init__(self, bucket, region, key, secret):
        self.bucket = bucket
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=key,
            aws_secret_access_key=secret,
            region_name=region,
        )

    def save(self, file, filename, app_name, version):
        s3_key = f"{app_name}/{version}/{filename}"
        self.s3.put_object(Bucket=self.bucket, Key=s3_key, Body=file)
        return f"s3://{self.bucket}/{s3_key}"

    def get(self, path: str, presign: bool = True):
        # path looks like s3://bucket/key
        _, _, bucket, *key_parts = path.split("/", 3)
        key = key_parts[-1] if key_parts else ""

        if presign:
            url = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=3600  # 1 hour
            )
            return {"url": url}

        # If you want to stream instead of presigned:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        self.s3.download_file(self.bucket, key, tmp.name)
        return FileResponse(tmp.name, filename=os.path.basename(key))


def get_storage():
    backend = os.getenv("STORAGE_BACKEND", "local").lower()
    if backend == "s3":
        return S3Storage(
            bucket=os.getenv("S3_BUCKET"),
            region=os.getenv("AWS_REGION"),
            key=os.getenv("AWS_ACCESS_KEY_ID"),
            secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
    else:
        return LocalStorage(os.getenv("LOCAL_STORAGE_PATH", "/app/uploads"))

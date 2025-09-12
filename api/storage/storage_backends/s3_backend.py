from fastapi.responses import FileResponse
import os
import boto3
import tempfile

from .base_backend import StorageBackend


class S3Storage(StorageBackend):
    STORAGE_TYPE: str = "s3"

    def __init__(self, bucket, region, key, secret):
        self.bucket = bucket or os.getenv("S3_BUCKET")
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=key or os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=secret or os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region or os.getenv("AWS_REGION"),
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

# main.py
from email.mime import base
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import boto3
import os

from models import LocationOut, VersionOut, ApplicationOut
from db import PostgresConnection
from storage import get_storage


storage = get_storage()
app = FastAPI()

# API endpoints
@app.get("/applications", response_model=List[ApplicationOut])
def get_applications():
    with PostgresConnection as cur:
        cur.execute("SELECT id, name FROM applications")
        apps = cur.fetchall()
        result = []
        for app_id, name in apps:
            cur.execute("""
                SELECT id, version FROM versions WHERE application_id=%s
            """, (app_id,))
            versions_data = cur.fetchall()
            versions_list = []
            for version_id, version_name in versions_data:
                cur.execute("SELECT path FROM locations WHERE version_id=%s", (version_id,))
                locations = [LocationOut(path=p[0]) for p in cur.fetchall()]
                versions_list.append(VersionOut(version=version_name, locations=locations))
            result.append(ApplicationOut(id=app_id, name=name, versions=versions_list))
    return result

@app.post("/upload")
async def upload_file(
    application_name: str = Form(...),
    version: str = Form(...),
    file: UploadFile = File(...)
):
    file_bytes = await file.read()
    saved_path = storage.save(file_bytes, file.filename, application_name, version)

    # Save metadata in DB
    with PostgresConnection() as cur:
        # Insert app
        cur.execute("INSERT INTO applications (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;", (application_name,))
        app_row = cur.fetchone()
        if app_row:
            app_id = app_row[0]
        else:
            cur.execute("SELECT id FROM applications WHERE name=%s", (application_name,))
            app_id = cur.fetchone()[0]

        # Insert version
        cur.execute("INSERT INTO versions (version, application_id) VALUES (%s, %s) RETURNING id;", (version, app_id))
        version_id = cur.fetchone()[0]

        # Insert location
        cur.execute("INSERT INTO locations (path, version_id) VALUES (%s, %s);", (saved_path, version_id))

    return {"message": "File uploaded", "path": saved_path}

@app.get("/download-version-dir/{application_name}/{version}")
def download_version_dir(application_name: str, version: str, presign: bool = Query(True)):
    with PostgresConnection() as cur:
        cur.execute("""
            SELECT l.path
            FROM applications a
            JOIN versions v ON a.id = v.application_id
            JOIN locations l ON v.id = l.version_id
            WHERE a.name = %s AND v.version = %s
            ORDER BY l.id LIMIT 1;
        """, (application_name, version))
        row = cur.fetchone()


    if not row:
        raise HTTPException(status_code=404, detail="File not found")

    path = row[0]
    return storage.get(path) if os.getenv("STORAGE_BACKEND") == "local" else storage.get(path, presign=presign)

@app.get("/download-app/{application_name}/{version}")
def download_app(application_name: str, version: str):
    with PostgresConnection() as cur:
        cur.execute("""
            SELECT l.path
            FROM applications a
            JOIN versions v ON a.id = v.application_id
            JOIN locations l ON v.id = l.version_id
            WHERE a.name = %s AND v.version = %s
            ORDER BY l.id LIMIT 1;
        """, (application_name, version))
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="No files found for this version")

    base_path = row[0]

    if storage.STORAGE_TYPE == "local":
        # If the path is a folder, find the first file inside
        if os.path.isdir(base_path):
            files = [f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))]
            if not files:
                raise HTTPException(status_code=404, detail="No files found in version folder")
            file_path = os.path.join(base_path, files[0])
        else:
            file_path = base_path

        # Use the actual file name for download
        filename = os.path.basename(file_path)
        return FileResponse(file_path, filename=filename)

    elif storage.STORAGE_TYPE == "s3":  # S3 backend
        s3 = storage.s3
        # Expect base_path like s3://bucket/key/prefix or full file path
        if base_path.endswith("/"):  # folder
            bucket, key_prefix = base_path.replace("s3://", "").split("/", 1)
            resp = s3.list_objects_v2(Bucket=bucket, Prefix=key_prefix)
            if "Contents" not in resp or not resp["Contents"]:
                raise HTTPException(status_code=404, detail="No files in version folder")
            # pick first actual file
            keys = [obj["Key"] for obj in resp["Contents"] if not obj["Key"].endswith("/")]
            if not keys:
                raise HTTPException(status_code=404, detail="No files found in version folder")
            key = keys[0]
        else:  # single file
            bucket, key = base_path.replace("s3://", "").split("/", 1)

        # Generate presigned URL
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600
        )
        return {"url": url, "filename": os.path.basename(key)}
    else:
        raise Exception(f"Invalid storage backend {storage.STORAGE_TYPE}")

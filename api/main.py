# main.py
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

import os

DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),  # name of your postgres container in Docker Compose
    "port": os.environ.get("DB_PORT")
}

app = FastAPI()

# Pydantic models
class LocationOut(BaseModel):
    path: str

class VersionOut(BaseModel):
    version: str
    locations: List[LocationOut]

class ApplicationOut(BaseModel):
    id: int
    name: str
    versions: List[VersionOut] = []

# DB helper
def get_conn():
    return psycopg2.connect(**DB_CONFIG)

# API endpoints
@app.get("/applications", response_model=List[ApplicationOut])
def get_applications():
    conn = get_conn()
    cur = conn.cursor()
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
    cur.close()
    conn.close()
    return result

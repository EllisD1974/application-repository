# Pydantic models
from pydantic import BaseModel
from typing import List, Optional


class LocationOut(BaseModel):
    path: str


class VersionOut(BaseModel):
    version: str
    locations: List[LocationOut]


class ApplicationOut(BaseModel):
    id: int
    name: str
    versions: List[VersionOut] = []


class LogCreate(BaseModel):
    version: str
    ticket: Optional[str] = None
    description: str
    visible: bool = True


class LogRead(LogCreate):
    id: int
    version_id: int

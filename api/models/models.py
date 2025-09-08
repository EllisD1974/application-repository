# Pydantic models
from pydantic import BaseModel
from typing import List


class LocationOut(BaseModel):
    path: str

class VersionOut(BaseModel):
    version: str
    locations: List[LocationOut]

class ApplicationOut(BaseModel):
    id: int
    name: str
    versions: List[VersionOut] = []

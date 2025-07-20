from pydantic import BaseModel, UUID4
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    Development = "Development"
    Active = "Active"
    Inactive = "Inactive"
    Archived = "Archived"

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    status: ProjectStatus = ProjectStatus.Development
    tags: List[str] = []
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    metrics: Dict = {}
    created_by: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: UUID4
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True

class AdminBase(BaseModel):
    sso_id: str

class AdminCreate(AdminBase):
    pass

class Admin(AdminBase):
    added_at: datetime

    class Config:
        from_attributes = True
        
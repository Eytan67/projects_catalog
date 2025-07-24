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
    detailed_description: Optional[str] = None
    category: Optional[str] = None
    status: ProjectStatus = ProjectStatus.Development
    tags: List[str] = []
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    metrics: Dict = {}
    created_by: Optional[str] = None
    tech_stack: List[str] = []
    team_name: Optional[str] = None
    product_manager: Optional[str] = None
    external_url: Optional[str] = None
    performance_metrics: Optional[str] = None
    objectives: Optional[str] = None
    challenges: Optional[str] = None
    future_plans: Optional[str] = None

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
    is_active: bool

    class Config:
        from_attributes = True
        
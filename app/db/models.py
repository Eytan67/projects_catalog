from sqlalchemy import Column, String, Text, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from db.database import Base
import enum
import uuid

class ProjectStatus(enum.Enum):
    Development = "Development"
    Active = "Active"
    Inactive = "Inactive"
    Archived = "Archived"

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    status = Column(Enum(ProjectStatus), default=ProjectStatus.Development)
    tags = Column(JSONB, default=list)
    image_path = Column(String(255))
    image_url = Column(String(500))
    metrics = Column(JSONB, default=dict)
    created_by = Column(String(100))
    created_date = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_date = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class Admin(Base):
    __tablename__ = "admins"

    sso_id = Column(String(100), primary_key=True)
    added_at = Column(TIMESTAMP, server_default=func.current_timestamp())
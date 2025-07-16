from sqlalchemy.orm import Session
from db.models import Project
from db.schemas import ProjectCreate, Project
from typing import List

def create_project(db: Session, project: ProjectCreate, created_by: str) -> Project:
    db_project = Project(**project.model_dump(), created_by=created_by)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: str) -> Project:
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    return db.query(Project).offset(skip).limit(limit).all()

def update_project(db: Session, project_id: str, project_update: ProjectCreate) -> Project:
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        return None
    for key, value in project_update.model_dump(exclude_unset=True).items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: str) -> bool:
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        return False
    db.delete(db_project)
    db.commit()
    return True

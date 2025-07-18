from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import ProjectCreate, Project
from services.project_service import create_project, get_project, get_projects, update_project, delete_project
from deps import is_admin
from db.models import Admin
from typing import List

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_new_project(
    project: ProjectCreate,
    current_user: Admin = Depends(is_admin),
    db: Session = Depends(get_db)
):
    return create_project(db, project, created_by=current_user.sso_id)

@router.get("/{project_id}", response_model=Project)
def read_project(project_id: str, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

@router.get("/", response_model=List[Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_projects(db, skip, limit)

@router.put("/{project_id}", response_model=Project)
def update_existing_project(
    project_id: str,
    project: ProjectCreate,
    current_user: Admin = Depends(is_admin),
    db: Session = Depends(get_db)
):
    updated_project = update_project(db, project_id, project)
    if not updated_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_project(
    project_id: str,
    current_user: Admin = Depends(is_admin),
    db: Session = Depends(get_db)
):
    success = delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

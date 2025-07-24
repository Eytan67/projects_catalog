from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.db.database import get_db
from app.db.schemas import ProjectCreate, Project
from app.services.project_service import create_project, get_project, get_projects, update_project, delete_project
from app.services.s3_service import s3_service
from app.services.s3_mock import mock_s3_service
from app.core.config import settings
from app.api.deps import is_admin
from app.db.models import Admin

router = APIRouter()

# Choose S3 service based on configuration
current_s3_service = mock_s3_service if settings.USE_MOCK_S3 else s3_service

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    project_data: str = Form(..., description="Project data as JSON string"),
    image: Optional[UploadFile] = File(None, description="Project image file"),
    _: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Create a new project with optional image upload"""
    try:
        # Parse JSON data from form
        project_dict = json.loads(project_data)
        project = ProjectCreate(**project_dict)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid JSON in project_data"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid project data: {str(e)}"
        )
    
    # Create project first to get ID
    db_project = create_project(db, project)
    
    # Upload image if provided
    if image and image.filename:
        try:
            image_url = await current_s3_service.upload_image(image, str(db_project.id))
            # Update project with image URL
            db_project.image_url = image_url
            db.commit()
            db.refresh(db_project)
        except Exception as e:
            # If image upload fails, we can still keep the project
            # but log the error or handle as needed
            print(f"Image upload failed: {str(e)}")
    
    return db_project

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
async def update_existing_project(
    project_id: str,
    project_data: str = Form(..., description="Project data as JSON string"),
    image: Optional[UploadFile] = File(None, description="New project image file"),
    _: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Update an existing project with optional new image upload"""
    try:
        # Parse JSON data from form
        project_dict = json.loads(project_data)
        project = ProjectCreate(**project_dict)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid JSON in project_data"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid project data: {str(e)}"
        )
    
    # Get existing project to check for old image
    existing_project = get_project(db, project_id)
    if not existing_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Upload new image if provided
    if image and image.filename:
        try:
            # Delete old image if exists
            if existing_project.image_url:
                current_s3_service.delete_image(existing_project.image_url)
            
            # Upload new image
            image_url = await current_s3_service.upload_image(image, project_id)
            project.image_url = image_url
        except Exception as e:
            print(f"Image upload failed: {str(e)}")
    
    # Update project
    updated_project = update_project(db, project_id, project)
    if not updated_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_project(
    project_id: str,
    _: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Delete a project and its associated image from S3"""
    # Get project to check for image
    existing_project = get_project(db, project_id)
    if not existing_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Delete image from storage if exists
    if existing_project.image_url:
        try:
            current_s3_service.delete_image(existing_project.image_url)
        except Exception as e:
            print(f"Failed to delete image from storage: {str(e)}")
    
    # Delete project from database
    success = delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

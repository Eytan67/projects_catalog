from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import get_db
from app.db.models import Admin as AdminModel

router = APIRouter()

@router.get("/check")
def check_admin_status(
    sso_id: Annotated[str, Query(description="SSO ID to check admin status")],
    db: Session = Depends(get_db)
):
    """Check if user with given sso_id is an admin"""
    admin = db.query(AdminModel).filter(
        AdminModel.sso_id == sso_id,
        AdminModel.is_active == True
    ).first()
    
    return {"is_admin": admin is not None}
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import get_db
from app.db.models import Admin as AdminModel

def is_admin(
    sso_id: Annotated[str, Query(description="SSO ID for admin verification")],
    db: Session = Depends(get_db),
) -> bool:
    if not sso_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    admin = db.query(AdminModel).filter(
        AdminModel.sso_id == sso_id,
        AdminModel.is_active == True  # Now using Boolean type
    ).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return True

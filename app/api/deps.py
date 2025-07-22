from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import get_db
from app.db.models import Admin as AdminModel

def is_admin(
    db: Session = Depends(get_db),
    sso_id: Annotated[str | None, Query(description="Optional project type for authorization")] = None
) -> bool:
    admin = db.query(AdminModel).filter(AdminModel.sso_id == sso_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin with id {sso_id} not found"
        )
    return True

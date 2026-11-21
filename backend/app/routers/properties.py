from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.deps import get_db
from backend.app.schemas import PropertyOut
from common.models import Property

router = APIRouter(prefix="/api/properties", tags=["properties"])


@router.get("", response_model=list[PropertyOut])
def list_properties(db: Session = Depends(get_db)):
    return db.query(Property).order_by(Property.name).all()

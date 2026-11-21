from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.deps import get_db
from backend.app.schemas import PropertyBreakdownOut, WeeklySummaryOut
from backend.app.services.aggregation import property_breakdown, weekly_summary

router = APIRouter(prefix="/api/summary", tags=["summary"])


@router.get("/weekly", response_model=WeeklySummaryOut)
def get_weekly_summary(
    property_id: str | None = None,
    week_ending: date | None = None,
    db: Session = Depends(get_db),
):
    week_ending = week_ending or date.today()
    return weekly_summary(db, week_ending, property_id)


@router.get("/properties", response_model=list[PropertyBreakdownOut])
def get_property_breakdown(
    week_ending: date | None = None,
    db: Session = Depends(get_db),
):
    week_ending = week_ending or date.today()
    return property_breakdown(db, week_ending)

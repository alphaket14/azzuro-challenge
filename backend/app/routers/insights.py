from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.deps import get_db
from backend.app.schemas import InsightsTopicsOut, TrendsOut
from backend.app.services.aggregation import trend_buckets
from backend.app.services.insights_service import topic_insights

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/topics", response_model=InsightsTopicsOut)
def get_topic_insights(
    week_ending: date | None = None,
    db: Session = Depends(get_db),
):
    week_ending = week_ending or date.today()
    return topic_insights(db, week_ending)


@router.get("/trends", response_model=TrendsOut)
def get_trends(
    property_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    granularity: str = "week",
    db: Session = Depends(get_db),
):
    date_to = date_to or date.today()
    date_from = date_from or date.today().replace(day=1)
    buckets = trend_buckets(db, date_from, date_to, granularity, property_id)
    return {"buckets": buckets}

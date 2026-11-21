from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from backend.app.deps import get_db
from backend.app.schemas import ReviewListOut, ReviewOut, TopicOut
from common.models import Review, ReviewTopic

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("", response_model=ReviewListOut)
def list_reviews(
    property_id: list[str] | None = Query(default=None),
    date_from: date | None = None,
    date_to: date | None = None,
    sentiment: str | None = None,
    topic: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Review).options(joinedload(Review.topics), joinedload(Review.property))

    if property_id:
        query = query.filter(Review.property_id.in_(property_id))
    if date_from:
        query = query.filter(Review.review_date >= date_from)
    if date_to:
        query = query.filter(Review.review_date <= date_to)
    if sentiment:
        query = query.filter(Review.sentiment == sentiment)
    if topic:
        query = query.join(ReviewTopic).filter(ReviewTopic.topic == topic)

    total = query.distinct(Review.id).count() if topic else query.count()

    query = query.order_by(Review.review_date.desc().nullslast(), Review.id.desc())
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return ReviewListOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[_to_review_out(r) for r in items],
    )


def _to_review_out(review: Review) -> ReviewOut:
    return ReviewOut(
        id=review.id,
        property_id=review.property_id,
        property_name=review.property.name if review.property else review.property_id,
        reviewer_name=review.reviewer_name,
        reviewer_country=review.reviewer_country,
        rating_raw=review.rating_raw,
        rating_normalized=review.rating_normalized,
        review_title=review.review_title,
        positive_text=review.positive_text,
        negative_text=review.negative_text,
        full_text=review.full_text,
        review_date=review.review_date,
        room_type=review.room_type,
        length_of_stay=review.length_of_stay,
        sentiment=review.sentiment,
        topics=[TopicOut(topic=t.topic, confidence=t.confidence) for t in review.topics],
    )

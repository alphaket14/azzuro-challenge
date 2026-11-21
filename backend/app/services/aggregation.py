"""Pure aggregation helpers over Review rows, kept separate from route
handlers so they're independently unit-testable (see backend/tests)."""

from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from common.models import Property, Review


def week_bounds(week_ending: date) -> tuple[date, date]:
    """Return (start, end) for the Mon-Sun week containing week_ending."""
    start = week_ending - timedelta(days=week_ending.weekday())
    end = start + timedelta(days=6)
    return start, end


def previous_week_bounds(week_ending: date) -> tuple[date, date]:
    start, _ = week_bounds(week_ending)
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=6)
    return prev_start, prev_end


def avg_rating_and_count(
    session: Session, start: date, end: date, property_id: str | None = None
) -> tuple[float | None, int]:
    query = session.query(func.avg(Review.rating_raw), func.count(Review.id)).filter(
        Review.review_date >= start, Review.review_date <= end
    )
    if property_id:
        query = query.filter(Review.property_id == property_id)
    avg_rating, count = query.one()
    return (round(avg_rating, 2) if avg_rating is not None else None), count


def weekly_summary(session: Session, week_ending: date, property_id: str | None = None) -> dict:
    cur_start, cur_end = week_bounds(week_ending)
    prev_start, prev_end = previous_week_bounds(week_ending)

    cur_avg, cur_count = avg_rating_and_count(session, cur_start, cur_end, property_id)
    prev_avg, prev_count = avg_rating_and_count(session, prev_start, prev_end, property_id)

    delta = None
    delta_pct = None
    if cur_avg is not None and prev_avg is not None:
        delta = round(cur_avg - prev_avg, 2)
        if prev_avg != 0:
            delta_pct = round((delta / prev_avg) * 100, 1)

    return {
        "current_week": {"start": cur_start, "end": cur_end, "avg_rating": cur_avg, "review_count": cur_count},
        "previous_week": {"start": prev_start, "end": prev_end, "avg_rating": prev_avg, "review_count": prev_count},
        "delta": delta,
        "delta_pct": delta_pct,
    }


def property_breakdown(session: Session, week_ending: date) -> list[dict]:
    cur_start, cur_end = week_bounds(week_ending)
    prev_start, prev_end = previous_week_bounds(week_ending)

    breakdown = []
    for prop in session.query(Property).order_by(Property.name).all():
        cur_avg, cur_count = avg_rating_and_count(session, cur_start, cur_end, prop.id)
        prev_avg, _ = avg_rating_and_count(session, prev_start, prev_end, prop.id)
        delta = round(cur_avg - prev_avg, 2) if (cur_avg is not None and prev_avg is not None) else None
        breakdown.append(
            {
                "property_id": prop.id,
                "property_name": prop.name,
                "avg_rating": cur_avg,
                "review_count": cur_count,
                "prev_avg_rating": prev_avg,
                "delta": delta,
            }
        )
    return breakdown


def trend_buckets(
    session: Session,
    date_from: date,
    date_to: date,
    granularity: str = "week",
    property_id: str | None = None,
) -> list[dict]:
    query = session.query(Review).filter(Review.review_date >= date_from, Review.review_date <= date_to)
    if property_id:
        query = query.filter(Review.property_id == property_id)

    buckets: dict[date, dict[str, int]] = {}
    for review in query.all():
        if review.review_date is None:
            continue
        if granularity == "day":
            bucket_start = review.review_date
        else:
            bucket_start = review.review_date - timedelta(days=review.review_date.weekday())

        bucket = buckets.setdefault(bucket_start, {"positive": 0, "neutral": 0, "negative": 0})
        bucket[review.sentiment] = bucket.get(review.sentiment, 0) + 1

    return [
        {"period_start": start, **counts}
        for start, counts in sorted(buckets.items())
    ]

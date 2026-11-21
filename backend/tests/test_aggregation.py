from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.services.aggregation import property_breakdown, week_bounds, weekly_summary
from common.models import Base, Property, Review


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()


def _add_review(db, property_id, review_date, rating, sentiment="neutral"):
    db.add(
        Review(
            property_id=property_id,
            review_hash=f"{property_id}-{review_date}-{rating}-{sentiment}-{id(object())}",
            full_text="sample",
            rating_raw=rating,
            review_date=review_date,
            sentiment=sentiment,
        )
    )


def test_week_bounds_returns_monday_to_sunday():
    start, end = week_bounds(date(2026, 11, 21))  # a Saturday
    assert start.weekday() == 0
    assert end.weekday() == 6
    assert start <= date(2026, 11, 21) <= end


def test_weekly_summary_computes_delta(session):
    session.add(Property(id="p1", name="Hotel One", booking_url="https://example.com"))
    _add_review(session, "p1", date(2026, 11, 18), 9.0)
    _add_review(session, "p1", date(2026, 11, 19), 7.0)
    _add_review(session, "p1", date(2026, 11, 11), 6.0)
    session.commit()

    result = weekly_summary(session, date(2026, 11, 21))
    assert result["current_week"]["avg_rating"] == 8.0
    assert result["current_week"]["review_count"] == 2
    assert result["previous_week"]["avg_rating"] == 6.0
    assert result["delta"] == 2.0


def test_property_breakdown_includes_all_properties(session):
    session.add(Property(id="p1", name="Hotel One", booking_url="https://example.com"))
    session.add(Property(id="p2", name="Hotel Two", booking_url="https://example.com"))
    _add_review(session, "p1", date(2026, 11, 18), 9.0)
    session.commit()

    breakdown = property_breakdown(session, date(2026, 11, 21))
    assert {b["property_id"] for b in breakdown} == {"p1", "p2"}
    p2 = next(b for b in breakdown if b["property_id"] == "p2")
    assert p2["review_count"] == 0
    assert p2["avg_rating"] is None

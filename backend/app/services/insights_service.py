"""Aggregates already-computed (scrape/seed-time) topic tags + sentiment
into the weekly "% of negative reviews mentioning topic X" insight shape,
plus simple rule-based headline sentences. No classification happens here -
that was already done once by common.topics and stored on Review/ReviewTopic."""

from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session

from common.models import Property, Review, ReviewTopic
from backend.app.services.aggregation import week_bounds

HEADLINE_THRESHOLD_PCT = 25.0


def _topic_breakdown_for_reviews(session: Session, review_ids: list[int]) -> tuple[list[dict], int]:
    if not review_ids:
        return [], 0

    negative_ids = {
        r.id
        for r in session.query(Review.id).filter(Review.id.in_(review_ids), Review.sentiment == "negative").all()
    }
    negative_total = len(negative_ids)

    counts: dict[str, int] = defaultdict(int)
    if negative_ids:
        rows = (
            session.query(ReviewTopic.topic)
            .filter(ReviewTopic.review_id.in_(negative_ids))
            .all()
        )
        for (topic,) in rows:
            counts[topic] += 1

    breakdown = [
        {
            "topic": topic,
            "negative_mentions": count,
            "negative_total": negative_total,
            "pct_of_negative": round((count / negative_total) * 100, 1) if negative_total else 0.0,
        }
        for topic, count in sorted(counts.items(), key=lambda kv: -kv[1])
    ]
    return breakdown, negative_total


def topic_insights(session: Session, week_ending: date) -> dict:
    start, end = week_bounds(week_ending)

    all_ids = [
        r.id for r in session.query(Review.id).filter(Review.review_date >= start, Review.review_date <= end).all()
    ]
    overall, _ = _topic_breakdown_for_reviews(session, all_ids)

    by_property: dict[str, list[dict]] = {}
    property_names: dict[str, str] = {}
    for prop in session.query(Property).all():
        property_names[prop.id] = prop.name
        prop_ids = [
            r.id
            for r in session.query(Review.id)
            .filter(
                Review.property_id == prop.id,
                Review.review_date >= start,
                Review.review_date <= end,
            )
            .all()
        ]
        breakdown, _ = _topic_breakdown_for_reviews(session, prop_ids)
        if breakdown:
            by_property[prop.id] = breakdown

    callouts = _headline_callouts(overall, by_property, property_names)

    return {
        "period": {"start": start, "end": end},
        "overall": overall,
        "by_property": by_property,
        "headline_callouts": callouts,
    }


def _headline_callouts(
    overall: list[dict], by_property: dict[str, list[dict]], property_names: dict[str, str]
) -> list[str]:
    callouts: list[str] = []

    for entry in overall:
        if entry["pct_of_negative"] >= HEADLINE_THRESHOLD_PCT and entry["negative_total"] > 0:
            callouts.append(
                f"{entry['pct_of_negative']:.0f}% of negative reviews this week mentioned "
                f"{entry['topic'].replace('_', ' ')}-related issues."
            )

    for property_id, breakdown in by_property.items():
        name = property_names.get(property_id, property_id)
        for entry in breakdown:
            if entry["pct_of_negative"] >= HEADLINE_THRESHOLD_PCT and entry["negative_total"] > 0:
                callouts.append(
                    f"{entry['pct_of_negative']:.0f}% of negative reviews at {name} this week mentioned "
                    f"{entry['topic'].replace('_', ' ')}-related issues."
                )

    return callouts[:5]

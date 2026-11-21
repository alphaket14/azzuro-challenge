"""Load data/sample_reviews.json into a fresh SQLite DB.

This is the path used for local demos/grading so that a working dashboard
never depends on live scraping succeeding. It reuses the exact same
dedup-hash and sentiment/topic fields that were computed by the scraper at
collection time (stored in the JSON), so behavior matches a live run.

Usage:
    python scripts/seed_db.py [--reset]
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common import config  # noqa: E402
from common.db import get_engine, init_db, session_scope  # noqa: E402
from common.models import Base, Property, Review, ReviewTopic  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the local SQLite DB from sample_reviews.json")
    parser.add_argument(
        "--reset", action="store_true", help="Drop and recreate all tables before seeding"
    )
    parser.add_argument(
        "--source",
        default=str(config.SAMPLE_REVIEWS_PATH),
        help="Path to the sample reviews JSON file",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if args.reset:
        Base.metadata.drop_all(get_engine())
    init_db()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"No sample data found at {source_path}. Run the scraper first, or check the path.")
        return 1

    with open(source_path, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    inserted = 0
    skipped = 0

    with session_scope() as session:
        for property_cfg in config.PROPERTIES:
            if session.get(Property, property_cfg.id) is None:
                session.add(
                    Property(id=property_cfg.id, name=property_cfg.name, booking_url=property_cfg.booking_url)
                )

        existing_hashes = {row[0] for row in session.query(Review.review_hash).all()}

        for review in reviews:
            if review["review_hash"] in existing_hashes:
                skipped += 1
                continue

            orm_review = Review(
                property_id=review["property_id"],
                review_hash=review["review_hash"],
                reviewer_name=review.get("reviewer_name"),
                reviewer_country=review.get("reviewer_country"),
                rating_raw=review.get("rating_raw"),
                rating_normalized=review.get("rating_normalized"),
                review_title=review.get("review_title"),
                positive_text=review.get("positive_text"),
                negative_text=review.get("negative_text"),
                full_text=review["full_text"],
                review_date=date.fromisoformat(review["review_date"]) if review.get("review_date") else None,
                room_type=review.get("room_type"),
                length_of_stay=review.get("length_of_stay"),
                sentiment=review.get("sentiment", "neutral"),
                sentiment_score=review.get("sentiment_score", 0.0),
            )
            session.add(orm_review)
            session.flush()

            for topic in review.get("topics", []):
                session.add(
                    ReviewTopic(
                        review_id=orm_review.id,
                        topic=topic["topic"],
                        confidence=topic["confidence"],
                        matched_phrases=json.dumps(topic["matched_phrases"]),
                    )
                )

            existing_hashes.add(review["review_hash"])
            inserted += 1

    print(f"Seeded {inserted} reviews ({skipped} already present, skipped).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

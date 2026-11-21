"""CLI entry point for the Booking.com review scraper.

Usage:
    python -m scraper.run --properties all --max-pages 20
    python -m scraper.run --properties olympic-paddington,venus-potts-point \\
        --max-pages 5 --export-json data/sample_reviews.json

See README.md "Review collection method & limitations" for the full
reliability/approach writeup.
"""

import argparse
import json
import logging
import sys
from datetime import date, datetime

from common import config
from common.db import init_db, session_scope
from common.models import Property, Review, ReviewTopic
from scraper.browser import BrowserSession
from scraper.logging_config import configure_logging
from scraper.property_scraper import scrape_property

logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape Booking.com reviews for Azzurro properties")
    parser.add_argument(
        "--properties",
        default="all",
        help="Comma-separated property ids, or 'all' (default) for every configured property",
    )
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--force-full-rescan", action="store_true")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.add_argument("--delay-min", type=float, default=1.5)
    parser.add_argument("--delay-max", type=float, default=3.5)
    parser.add_argument(
        "--export-json",
        default=None,
        help="If set, also write newly collected reviews to this JSON file (merged with any existing entries)",
    )
    return parser.parse_args()


def _resolve_properties(selection: str) -> list[config.PropertyConfig]:
    if selection == "all":
        return config.PROPERTIES
    ids = {p.strip() for p in selection.split(",") if p.strip()}
    unknown = ids - set(config.PROPERTIES_BY_ID)
    if unknown:
        raise SystemExit(f"Unknown property id(s): {', '.join(sorted(unknown))}")
    return [config.PROPERTIES_BY_ID[i] for i in ids]


def _ensure_properties_row(session, property_cfg: config.PropertyConfig) -> None:
    existing = session.get(Property, property_cfg.id)
    if existing is None:
        session.add(Property(id=property_cfg.id, name=property_cfg.name, booking_url=property_cfg.booking_url))


def _load_existing_hashes(session) -> set[str]:
    return {row[0] for row in session.query(Review.review_hash).all()}


def _persist_reviews(session, reviews: list[dict]) -> None:
    for review in reviews:
        orm_review = Review(
            property_id=review["property_id"],
            review_hash=review["review_hash"],
            reviewer_name=review["reviewer_name"],
            reviewer_country=review["reviewer_country"],
            rating_raw=review["rating_raw"],
            rating_normalized=review["rating_normalized"],
            review_title=review["review_title"],
            positive_text=review["positive_text"],
            negative_text=review["negative_text"],
            full_text=review["full_text"],
            review_date=date.fromisoformat(review["review_date"]) if review["review_date"] else None,
            room_type=review["room_type"],
            length_of_stay=review["length_of_stay"],
            sentiment=review["sentiment"],
            sentiment_score=review["sentiment_score"],
        )
        session.add(orm_review)
        session.flush()  # assign orm_review.id

        for topic in review["topics"]:
            session.add(
                ReviewTopic(
                    review_id=orm_review.id,
                    topic=topic["topic"],
                    confidence=topic["confidence"],
                    matched_phrases=json.dumps(topic["matched_phrases"]),
                )
            )


def _export_json(path: str, new_reviews: list[dict]) -> None:
    existing: list[dict] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []

    existing_hashes = {r["review_hash"] for r in existing}
    merged = existing + [r for r in new_reviews if r["review_hash"] not in existing_hashes]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, default=str)

    logger.info("Exported %d total reviews to %s (%d new)", len(merged), path, len(new_reviews))


def main() -> int:
    args = _parse_args()
    log_path = configure_logging()
    logger.info("Scrape run starting; logging to %s", log_path)

    properties = _resolve_properties(args.properties)
    init_db()

    all_new_reviews: list[dict] = []
    summaries = []

    with session_scope() as session:
        for property_cfg in properties:
            _ensure_properties_row(session, property_cfg)
        existing_hashes = _load_existing_hashes(session)

    with BrowserSession(headless=args.headless) as browser:
        for property_cfg in properties:
            logger.info("Scraping %s (%s)", property_cfg.name, property_cfg.id)
            page = browser.new_page()
            try:
                result, new_reviews = scrape_property(
                    page=page,
                    property_cfg=property_cfg,
                    existing_hashes=existing_hashes,
                    max_pages=args.max_pages,
                    force_full_rescan=args.force_full_rescan,
                    delay_min=args.delay_min,
                    delay_max=args.delay_max,
                )
            finally:
                page.close()

            summaries.append(result)
            all_new_reviews.extend(new_reviews)

            with session_scope() as session:
                _persist_reviews(session, new_reviews)

    if args.export_json and all_new_reviews:
        _export_json(args.export_json, all_new_reviews)

    print("\n=== Scrape run summary ===")
    for result in summaries:
        status = "OK" if result.succeeded else "FAILED"
        print(
            f"[{status}] {result.property_id}: "
            f"{result.new_count} new, {result.skipped_duplicate_count} duplicates skipped, "
            f"{result.parse_failure_count} parse failures"
        )
        for error in result.errors:
            print(f"    error: {error}")
    print(f"Finished at {datetime.now().isoformat(timespec='seconds')}")

    all_failed = all(not r.succeeded for r in summaries)
    return 1 if all_failed else 0


if __name__ == "__main__":
    sys.exit(main())

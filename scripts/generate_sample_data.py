"""Generates data/sample_reviews.json: a synthetic but schema-accurate
sample dataset for the 4 Azzurro properties.

WHY THIS EXISTS: during build-time verification, the real scraper
(scraper/) was pointed at the live Booking.com pages and correctly
navigated to each property and clicked through to "Read all reviews" -
but Booking.com's bot-challenge system (requests to
`/__challenge_.../mp_verify`, `/__challenge_.../telemetry`, etc.) intercepted
the session before actual review content loaded. This is the exact
"Booking.com may block/CAPTCHA/rate-limit the scraper" risk documented in
README.md, observed directly rather than hypothetically.

To still deliver a working, demonstrable dashboard + insights pipeline,
this script produces REALISTIC BUT SYNTHETIC reviews, run through the exact
same hashing/classification/sentiment code path the live scraper uses
(common.hashing, common.topics), so the rest of the system - DB schema,
dedup, backend aggregation, frontend - is exercised identically to how it
would run on real scraped data. This is NOT scraped data and is labeled as
such; see README.md "Known limitations & assumptions".

Usage:
    python scripts/generate_sample_data.py
"""

import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common import config  # noqa: E402
from common.hashing import compute_review_hash  # noqa: E402
from common.topics import classify_review, derive_sentiment  # noqa: E402

random.seed(42)

REVIEWER_NAMES = [
    "Jane D.", "Marco R.", "Priya S.", "Liam O.", "Chen W.", "Sofia M.",
    "Noah B.", "Aisha K.", "Tom H.", "Yuki T.", "Emma L.", "Carlos G.",
    "Grace P.", "Daniel F.", "Mei L.", "Oliver N.", "Hana Y.", "Lucas V.",
]
COUNTRIES = ["Australia", "United Kingdom", "United States", "Singapore", "New Zealand", "Japan", "Germany", "India"]
ROOM_TYPES = ["Standard Double", "Deluxe Double", "Twin Room", "Queen Room", "Budget Single", "Family Room"]
LENGTHS_OF_STAY = ["1 night", "2 nights", "3 nights", "4 nights", "5 nights", "7 nights"]

# Each snippet is tagged with the rating range it's plausible for, so
# generated reviews stay internally consistent (a 9/10 review shouldn't be
# full of complaints, etc).
POSITIVE_SNIPPETS = [
    "The room was spotless and the bed was so comfortable.",
    "Staff were incredibly friendly and helpful throughout our stay.",
    "Great location, walking distance to everything we needed.",
    "Check-in was quick and smooth, no waiting around at all.",
    "Good value for money, especially for the location.",
    "The room was quiet and we slept really well.",
    "Facilities were great - loved the pool and gym.",
    "Lovely staff, went above and beyond to help us.",
    "Room was modern and well maintained, very comfortable.",
    "Perfectly located, close to all the main attractions.",
]
NEGATIVE_SNIPPETS = [
    "The room was dirty when we arrived and smelled musty.",
    "Staff at reception were rude and unhelpful when we asked for help.",
    "Very noisy at night, could hear traffic and other guests through thin walls.",
    "Check-in took forever, we waited almost 40 minutes with no one at reception.",
    "The air conditioning was not working and it was never fixed.",
    "Room felt outdated, with old furniture and a damaged bathroom door.",
    "Overpriced for what you get, poor value for money.",
    "Elevator was out of order for our entire stay, had to use the stairs.",
    "Hard to find and felt quite far from the city centre.",
    "Bathroom was not clean, found hair in the shower.",
]
NEUTRAL_SNIPPETS = [
    "Stay was okay overall, nothing particularly stood out.",
    "An average stay, met our basic expectations.",
    "Room was fine for a short stay, nothing special.",
]


def _pick_snippets(rating: float) -> tuple[str | None, str | None]:
    if rating >= 8:
        positive = random.choice(POSITIVE_SNIPPETS)
        negative = random.choice(NEGATIVE_SNIPPETS) if random.random() < 0.15 else None
    elif rating <= 5:
        negative = random.choice(NEGATIVE_SNIPPETS)
        positive = random.choice(POSITIVE_SNIPPETS) if random.random() < 0.15 else None
    else:
        positive = random.choice(POSITIVE_SNIPPETS) if random.random() < 0.5 else None
        negative = random.choice(NEGATIVE_SNIPPETS) if random.random() < 0.5 else None
        if positive is None and negative is None:
            positive = random.choice(NEUTRAL_SNIPPETS)
    return positive, negative


def _random_rating() -> float:
    # Skewed toward positive, as is typical for Booking.com review distributions.
    return round(random.choices(
        [random.uniform(8.5, 10.0), random.uniform(6.0, 8.4), random.uniform(2.0, 5.9)],
        weights=[0.55, 0.3, 0.15],
    )[0], 1)


def generate_reviews_for_property(property_cfg, count: int, today: date) -> list[dict]:
    reviews = []
    for _ in range(count):
        days_ago = random.randint(0, 35)  # spread across the last 5 weeks
        review_date = today - timedelta(days=days_ago)
        rating = _random_rating()
        positive_text, negative_text = _pick_snippets(rating)

        reviewer_name = random.choice(REVIEWER_NAMES)
        title_parts = []
        if positive_text:
            title_parts.append("Great stay" if rating >= 8 else "Decent stay")
        if negative_text and rating <= 5:
            title_parts = ["Disappointing stay"]
        review_title = title_parts[0] if title_parts else "Average stay"

        body_parts = [p for p in [review_title, positive_text, negative_text] if p]
        full_text = " ".join(body_parts)

        review_date_str = review_date.isoformat()
        review_hash = compute_review_hash(property_cfg.id, reviewer_name, review_date_str, full_text)

        sentiment, sentiment_score = derive_sentiment(rating, full_text)
        topic_matches = classify_review(full_text)

        reviews.append(
            {
                "property_id": property_cfg.id,
                "review_hash": review_hash,
                "reviewer_name": reviewer_name,
                "reviewer_country": random.choice(COUNTRIES),
                "rating_raw": rating,
                "rating_normalized": round(rating / 2, 2),
                "review_title": review_title,
                "positive_text": positive_text,
                "negative_text": negative_text,
                "full_text": full_text,
                "review_date": review_date_str,
                "room_type": random.choice(ROOM_TYPES),
                "length_of_stay": random.choice(LENGTHS_OF_STAY),
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "topics": [
                    {"topic": m.topic, "confidence": m.confidence, "matched_phrases": m.matched_phrases}
                    for m in topic_matches
                ],
            }
        )
    return reviews


def main() -> int:
    today = date.today()
    all_reviews = []
    for property_cfg in config.PROPERTIES:
        all_reviews.extend(generate_reviews_for_property(property_cfg, count=35, today=today))

    # De-duplicate just in case random generation produced a collision.
    seen = set()
    unique_reviews = []
    for r in all_reviews:
        if r["review_hash"] in seen:
            continue
        seen.add(r["review_hash"])
        unique_reviews.append(r)

    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.SAMPLE_REVIEWS_PATH, "w", encoding="utf-8") as f:
        json.dump(unique_reviews, f, indent=2, default=str)

    print(f"Generated {len(unique_reviews)} synthetic sample reviews to {config.SAMPLE_REVIEWS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

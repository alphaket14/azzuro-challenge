import hashlib


def compute_review_hash(
    property_id: str,
    reviewer_name: str | None,
    review_date: str | None,
    full_text: str,
) -> str:
    """Stable dedup key for a review.

    Booking.com does not expose a stable public review id, so identity is
    derived from content instead. Reviews are treated as immutable: if this
    hash already exists in the DB, the review is skipped on re-scrape/reseed.
    """
    parts = [property_id, reviewer_name or "", review_date or "", full_text.strip()]
    digest_input = "||".join(parts).encode("utf-8")
    return hashlib.sha256(digest_input).hexdigest()

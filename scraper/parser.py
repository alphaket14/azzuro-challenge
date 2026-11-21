import logging
import re
from dataclasses import dataclass
from datetime import date

from bs4 import BeautifulSoup, Tag
from dateutil import parser as dateutil_parser

from scraper import selectors
from scraper.logging_config import parse_failures_logger

logger = logging.getLogger(__name__)


@dataclass
class ParsedReview:
    reviewer_name: str | None
    reviewer_country: str | None
    rating_raw: float | None
    review_title: str | None
    positive_text: str | None
    negative_text: str | None
    full_text: str
    review_date: date | None
    room_type: str | None
    length_of_stay: str | None


def _first_match_text(node: Tag, selector_candidates: list[str]) -> str | None:
    for selector in selector_candidates:
        try:
            found = node.select_one(selector)
        except Exception:
            continue
        if found is not None:
            text = found.get_text(strip=True)
            if text:
                return text
    return None


def _parse_rating(node: Tag, property_id: str) -> float | None:
    try:
        raw = _first_match_text(node, selectors.RATING_BADGE)
        if raw is None:
            return None
        match = re.search(r"[\d.,]+", raw)
        if not match:
            return None
        return float(match.group(0).replace(",", "."))
    except Exception as exc:  # noqa: BLE001 - defensive per-field extraction
        parse_failures_logger.warning("[%s] failed to parse rating: %s", property_id, exc)
        return None


def _parse_date(node: Tag, property_id: str) -> date | None:
    try:
        raw = _first_match_text(node, selectors.REVIEW_DATE)
        if raw is None:
            return None
        cleaned = re.sub(r"^(reviewed|date of stay)[:\s]*", "", raw, flags=re.IGNORECASE).strip()
        return dateutil_parser.parse(cleaned, fuzzy=True).date()
    except Exception as exc:  # noqa: BLE001
        parse_failures_logger.warning("[%s] failed to parse review date %r: %s", property_id, raw if 'raw' in locals() else None, exc)
        return None


def parse_review_card(card_html: str, property_id: str) -> ParsedReview | None:
    """Defensively parse one review card. Each field is extracted in its own
    try/except so a single bad/missing field never drops the whole review -
    only a missing full_text causes the review to be skipped entirely."""
    node = BeautifulSoup(card_html, "lxml")

    reviewer_name = _first_match_text(node, selectors.REVIEWER_NAME)
    reviewer_country = _first_match_text(node, selectors.REVIEWER_COUNTRY)
    review_title = _first_match_text(node, selectors.REVIEW_TITLE)
    room_type = _first_match_text(node, selectors.ROOM_TYPE)
    length_of_stay = _first_match_text(node, selectors.LENGTH_OF_STAY)

    rating_raw = _parse_rating(node, property_id)
    review_date = _parse_date(node, property_id)

    positive_text = _first_match_text(node, selectors.REVIEW_POSITIVE_TEXT)
    negative_text = _first_match_text(node, selectors.REVIEW_NEGATIVE_TEXT)

    body_parts = [p for p in [review_title, positive_text, negative_text] if p]
    if not body_parts:
        fallback = _first_match_text(node, selectors.REVIEW_BODY_FALLBACK)
        if fallback:
            body_parts = [fallback]

    full_text = " ".join(body_parts).strip()
    if not full_text:
        parse_failures_logger.warning(
            "[%s] skipping review card with no extractable text (reviewer=%r)",
            property_id,
            reviewer_name,
        )
        return None

    return ParsedReview(
        reviewer_name=reviewer_name,
        reviewer_country=reviewer_country,
        rating_raw=rating_raw,
        review_title=review_title,
        positive_text=positive_text,
        negative_text=negative_text,
        full_text=full_text,
        review_date=review_date,
        room_type=room_type,
        length_of_stay=length_of_stay,
    )

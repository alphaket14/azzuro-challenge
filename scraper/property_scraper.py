import logging
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from playwright.sync_api import Page

from common import config
from common.hashing import compute_review_hash
from common.topics import classify_review, derive_sentiment
from scraper import selectors
from scraper.browser import dismiss_cookie_banner, find_first, goto_with_retry, polite_delay
from scraper.pagination import iter_review_pages
from scraper.parser import parse_review_card

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    property_id: str
    new_count: int = 0
    skipped_duplicate_count: int = 0
    parse_failure_count: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return not self.errors


def _try_sort_newest_first(page: Page) -> None:
    control = find_first(page, selectors.SORT_DROPDOWN)
    if control is None:
        logger.warning("Sort control not found; incremental early-stop may be less effective")
        return
    try:
        control.click(timeout=3000)
        for option_text in selectors.SORT_NEWEST_OPTION_TEXT_CANDIDATES:
            option = page.get_by_text(option_text, exact=False)
            if option.count() > 0:
                option.first.click(timeout=3000)
                page.wait_for_timeout(1000)
                return
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not set sort order to newest-first: %s", exc)


def scrape_property(
    page: Page,
    property_cfg: config.PropertyConfig,
    existing_hashes: set[str],
    max_pages: int,
    force_full_rescan: bool,
    delay_min: float,
    delay_max: float,
) -> tuple[ScrapeResult, list[dict]]:
    """Scrape one property end-to-end. Any unexpected exception is caught
    here so that one property's failure never aborts the whole run (the
    caller loops over properties and calls this per-property)."""
    result = ScrapeResult(property_id=property_cfg.id)
    collected_reviews: list[dict] = []

    try:
        if not goto_with_retry(page, property_cfg.booking_url):
            result.errors.append("Failed to load property page")
            return result, collected_reviews

        dismiss_cookie_banner(page)

        reviews_link = find_first(page, selectors.REVIEWS_TAB_LINK)
        if reviews_link is not None:
            try:
                reviews_link.click(timeout=5000)
                page.wait_for_timeout(1000)
            except Exception as exc:  # noqa: BLE001
                logger.warning("[%s] could not click reviews tab: %s", property_cfg.id, exc)

        _try_sort_newest_first(page)
        polite_delay(delay_min, delay_max)

        consecutive_seen = 0
        threshold = float("inf") if force_full_rescan else config.CONSECUTIVE_SEEN_THRESHOLD

        for page_html in iter_review_pages(
            page, property_cfg.booking_url, max_pages, delay_min, delay_max
        ):
            soup = BeautifulSoup(page_html, "lxml")
            cards = []
            for selector in selectors.REVIEW_CARD:
                cards = soup.select(selector)
                if cards:
                    break

            if not cards:
                logger.info("[%s] no review cards found on this page", property_cfg.id)
                continue

            for card in cards:
                parsed = parse_review_card(str(card), property_cfg.id)
                if parsed is None:
                    result.parse_failure_count += 1
                    continue

                review_date_str = parsed.review_date.isoformat() if parsed.review_date else ""
                review_hash = compute_review_hash(
                    property_cfg.id, parsed.reviewer_name, review_date_str, parsed.full_text
                )

                if review_hash in existing_hashes:
                    consecutive_seen += 1
                    result.skipped_duplicate_count += 1
                    if consecutive_seen >= threshold:
                        logger.info(
                            "[%s] stopping early after %d consecutive already-seen reviews",
                            property_cfg.id,
                            consecutive_seen,
                        )
                        return result, collected_reviews
                    continue

                consecutive_seen = 0
                existing_hashes.add(review_hash)

                sentiment, sentiment_score = derive_sentiment(parsed.rating_raw, parsed.full_text)
                topic_matches = classify_review(parsed.full_text)

                collected_reviews.append(
                    {
                        "property_id": property_cfg.id,
                        "review_hash": review_hash,
                        "reviewer_name": parsed.reviewer_name,
                        "reviewer_country": parsed.reviewer_country,
                        "rating_raw": parsed.rating_raw,
                        "rating_normalized": (parsed.rating_raw / 2) if parsed.rating_raw is not None else None,
                        "review_title": parsed.review_title,
                        "positive_text": parsed.positive_text,
                        "negative_text": parsed.negative_text,
                        "full_text": parsed.full_text,
                        "review_date": review_date_str or None,
                        "room_type": parsed.room_type,
                        "length_of_stay": parsed.length_of_stay,
                        "sentiment": sentiment,
                        "sentiment_score": sentiment_score,
                        "topics": [
                            {
                                "topic": m.topic,
                                "confidence": m.confidence,
                                "matched_phrases": m.matched_phrases,
                            }
                            for m in topic_matches
                        ],
                    }
                )
                result.new_count += 1

    except Exception as exc:  # noqa: BLE001 - per-property isolation
        logger.exception("[%s] unexpected error during scrape", property_cfg.id)
        result.errors.append(str(exc))

    return result, collected_reviews

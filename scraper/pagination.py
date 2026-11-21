import hashlib
import logging

from playwright.sync_api import Page

from scraper import selectors
from scraper.browser import find_first, goto_with_retry, polite_delay

logger = logging.getLogger(__name__)


def _first_card_fingerprint(page: Page) -> str | None:
    card = find_first(page, selectors.REVIEW_CARD)
    if card is None:
        return None
    try:
        text = card.inner_text(timeout=3000)
    except Exception:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def iter_review_pages(
    page: Page,
    base_url: str,
    max_pages: int,
    delay_min: float,
    delay_max: float,
):
    """Yield the page's HTML for each successive reviews page, up to
    max_pages. Tries a `page=N` query parameter first; if that does not
    actually change the visible content (checked via a content fingerprint),
    falls back to clicking a "load more" / "next page" control instead."""
    previous_fingerprint = None
    query_param_working = True

    for page_number in range(1, max_pages + 1):
        if page_number == 1:
            pass  # caller has already navigated to base_url for page 1
        elif query_param_working:
            separator = "&" if "?" in base_url else "?"
            url = f"{base_url}{separator}page={page_number}"
            if not goto_with_retry(page, url, wait_selector_candidates=selectors.REVIEW_CARD):
                logger.info("Stopping pagination: could not load page %d", page_number)
                return

        fingerprint = _first_card_fingerprint(page)

        if page_number > 1 and query_param_working and fingerprint == previous_fingerprint:
            # The page=N approach didn't change content - fall back to a
            # "load more"/next-page click for subsequent pages.
            query_param_working = False
            clicked = _click_next_or_load_more(page)
            if not clicked:
                logger.info("No next-page control found; stopping pagination at page %d", page_number)
                return
            fingerprint = _first_card_fingerprint(page)
            if fingerprint == previous_fingerprint:
                logger.info("Pagination control did not change content; stopping at page %d", page_number)
                return

        if fingerprint is None:
            logger.info("No review cards found on page %d; stopping pagination", page_number)
            return

        yield page.content()
        previous_fingerprint = fingerprint
        polite_delay(delay_min, delay_max)


def _click_next_or_load_more(page: Page) -> bool:
    for selector_group in (selectors.LOAD_MORE_BUTTON, selectors.NEXT_PAGE_BUTTON):
        control = find_first(page, selector_group)
        if control is not None:
            try:
                control.click(timeout=5000)
                page.wait_for_timeout(1000)
                return True
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed clicking pagination control: %s", exc)
    return False

import logging
import random
import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from scraper import selectors

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 2


class BrowserSession:
    """Thin wrapper around a single Playwright browser, reused across
    properties (cheaper than relaunching Chromium each time), handing out a
    fresh page per property to avoid cookie/filter state bleeding between
    properties."""

    def __init__(self, headless: bool = True):
        self._headless = headless
        self._playwright = None
        self._browser = None

    def __enter__(self) -> "BrowserSession":
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self._headless)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def new_page(self) -> Page:
        context = self._browser.new_context(user_agent=USER_AGENT, viewport={"width": 1366, "height": 900})
        return context.new_page()


def dismiss_cookie_banner(page: Page) -> None:
    for selector in selectors.COOKIE_CONSENT_BUTTON:
        try:
            locator = page.locator(selector)
            if locator.count() > 0 and locator.first.is_visible():
                locator.first.click(timeout=2000)
                return
        except Exception:
            continue


def goto_with_retry(page: Page, url: str, wait_selector_candidates: list[str] | None = None) -> bool:
    """Navigate to a URL with retry/backoff. Returns True on success."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            if wait_selector_candidates:
                found = False
                for sel in wait_selector_candidates:
                    try:
                        page.wait_for_selector(sel, timeout=8000)
                        found = True
                        break
                    except PlaywrightTimeoutError:
                        continue
                if not found:
                    logger.warning("No expected selector found on %s (attempt %d)", url, attempt)
            return True
        except PlaywrightTimeoutError as exc:
            logger.warning("Timeout loading %s (attempt %d/%d): %s", url, attempt, MAX_RETRIES, exc)
        except Exception as exc:  # noqa: BLE001 - want to retry on any transient navigation error
            logger.warning("Error loading %s (attempt %d/%d): %s", url, attempt, MAX_RETRIES, exc)

        if attempt < MAX_RETRIES:
            sleep_for = BACKOFF_BASE_SECONDS ** attempt
            time.sleep(sleep_for)

    logger.error("Giving up on %s after %d attempts", url, MAX_RETRIES)
    return False


def polite_delay(min_seconds: float, max_seconds: float) -> None:
    time.sleep(random.uniform(min_seconds, max_seconds))


def find_first(page: Page, selector_candidates: list[str]):
    for selector in selector_candidates:
        locator = page.locator(selector)
        try:
            if locator.count() > 0:
                return locator.first
        except Exception:
            continue
    return None

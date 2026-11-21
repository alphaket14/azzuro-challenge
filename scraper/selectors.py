"""Single source of truth for Booking.com DOM selectors used by the scraper.

Booking.com's markup changes periodically and differs across experiment
cohorts. Every selector here is a *list* of candidates, tried in order by
browser.try_selectors() / parser.py, so a layout change only needs a new
entry appended here rather than a code change scattered across the scraper.
These were verified empirically against the live site at build time
(November 2026) and are expected to need maintenance over time - see
README.md "Review collection method & limitations".
"""

COOKIE_CONSENT_BUTTON = [
    "#onetrust-accept-btn-handler",
    "button[data-testid='cookie-banner-accept']",
    "button[aria-label='Accept']",
]

REVIEWS_TAB_LINK = [
    "a[data-testid='PropertyHeaderReviewsLink']",
    "a[href*='#tab-reviews']",
    "a[href*='reviews']",
]

SORT_DROPDOWN = [
    "select[data-testid='sorter']",
    "button[data-testid='reviews-sort-button']",
    "#review_sort",
]

SORT_NEWEST_OPTION_TEXT_CANDIDATES = [
    "Newest first",
    "Most recent",
]

REVIEW_CARD = [
    "[data-testid='review-card']",
    "div.c-review-block",
    "div[data-review-url]",
]

REVIEWER_NAME = [
    "[data-testid='review-avatar'] .bui-avatar-block__title",
    ".c-review-block__guest-name",
    ".bui-avatar-block__title",
]

REVIEWER_COUNTRY = [
    "[data-testid='review-avatar'] span.bui-avatar-block__subtitle",
    ".bui-avatar-block__subtitle",
]

RATING_BADGE = [
    "[data-testid='review-score'] .bui-review-score__badge",
    ".c-score-bar__score",
    ".bui-review-score__badge",
]

REVIEW_TITLE = [
    "[data-testid='review-title']",
    ".c-review-block__title",
    "h3.c-review__title",
]

REVIEW_POSITIVE_TEXT = [
    "[data-testid='review-positive-text']",
    ".c-review__row--positive .c-review__body",
]

REVIEW_NEGATIVE_TEXT = [
    "[data-testid='review-negative-text']",
    ".c-review__row--negative .c-review__body",
]

REVIEW_BODY_FALLBACK = [
    "[data-testid='review-body']",
    ".c-review__body",
]

REVIEW_DATE = [
    "[data-testid='review-date']",
    ".c-review-block__date",
]

ROOM_TYPE = [
    "[data-testid='review-room-name']",
    ".c-review-block__room-info .bui-list__description",
]

LENGTH_OF_STAY = [
    "[data-testid='review-num-nights']",
    ".c-review-block__stay-info",
]

NEXT_PAGE_BUTTON = [
    "button[aria-label='Next page']",
    "a[data-testid='reviews-pagination-next']",
    ".bui-pagination__next-arrow a",
]

LOAD_MORE_BUTTON = [
    "button[data-testid='load-more-reviews']",
    "button.c-load-more",
]

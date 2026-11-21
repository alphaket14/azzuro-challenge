from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DB_PATH = DATA_DIR / "azzurro.db"
SAMPLE_REVIEWS_PATH = DATA_DIR / "sample_reviews.json"
TOPICS_CONFIG_PATH = Path(__file__).resolve().parent / "topics.yaml"


@dataclass(frozen=True)
class PropertyConfig:
    id: str
    name: str
    booking_url: str


PROPERTIES: list[PropertyConfig] = [
    PropertyConfig(
        id="olympic-paddington",
        name="Olympic Hotel Paddington",
        booking_url="https://www.booking.com/hotel/au/olympic-paddington.html",
    ),
    PropertyConfig(
        id="venus-potts-point",
        name="Potts Point",
        booking_url="https://www.booking.com/hotel/au/venus-potts-point-sydney.html",
    ),
    PropertyConfig(
        id="venus-surry-hills",
        name="Central Sydney",
        booking_url="https://www.booking.com/hotel/au/venus-surry-hills.html",
    ),
    PropertyConfig(
        id="chateau-de-venus",
        name="Darling Harbour",
        booking_url="https://www.booking.com/hotel/au/chateau-de-venus.html",
    ),
]

PROPERTIES_BY_ID: dict[str, PropertyConfig] = {p.id: p for p in PROPERTIES}

# Incremental-scrape behavior: once this many consecutive reviews (newest-first)
# are already present in the DB, stop paginating for that property.
CONSECUTIVE_SEEN_THRESHOLD = 5

# Sentiment thresholds, on Booking.com's native 0-10 rating scale.
SENTIMENT_POSITIVE_MIN = 8.0
SENTIMENT_NEGATIVE_MAX = 5.0

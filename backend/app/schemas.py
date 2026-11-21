from datetime import date

from pydantic import BaseModel


class PropertyOut(BaseModel):
    id: str
    name: str
    booking_url: str


class TopicOut(BaseModel):
    topic: str
    confidence: float


class ReviewOut(BaseModel):
    id: int
    property_id: str
    property_name: str
    reviewer_name: str | None
    reviewer_country: str | None
    rating_raw: float | None
    rating_normalized: float | None
    review_title: str | None
    positive_text: str | None
    negative_text: str | None
    full_text: str
    review_date: date | None
    room_type: str | None
    length_of_stay: str | None
    sentiment: str
    topics: list[TopicOut]


class ReviewListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ReviewOut]


class WeekSummary(BaseModel):
    start: date
    end: date
    avg_rating: float | None
    review_count: int


class WeeklySummaryOut(BaseModel):
    current_week: WeekSummary
    previous_week: WeekSummary
    delta: float | None
    delta_pct: float | None


class PropertyBreakdownOut(BaseModel):
    property_id: str
    property_name: str
    avg_rating: float | None
    review_count: int
    prev_avg_rating: float | None
    delta: float | None


class TopicInsight(BaseModel):
    topic: str
    negative_mentions: int
    negative_total: int
    pct_of_negative: float


class InsightsTopicsOut(BaseModel):
    period: dict[str, date]
    overall: list[TopicInsight]
    by_property: dict[str, list[TopicInsight]]
    headline_callouts: list[str]


class TrendBucket(BaseModel):
    period_start: date
    positive: int
    neutral: int
    negative: int


class TrendsOut(BaseModel):
    buckets: list[TrendBucket]

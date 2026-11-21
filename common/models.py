from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    booking_url: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    reviews: Mapped[list["Review"]] = relationship(back_populates="property")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        Index("ix_reviews_property_date", "property_id", "review_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    property_id: Mapped[str] = mapped_column(ForeignKey("properties.id"), nullable=False)
    review_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    reviewer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewer_country: Mapped[str | None] = mapped_column(String, nullable=True)

    rating_raw: Mapped[float | None] = mapped_column(Float, nullable=True)
    rating_normalized: Mapped[float | None] = mapped_column(Float, nullable=True)

    review_title: Mapped[str | None] = mapped_column(String, nullable=True)
    positive_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    negative_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)

    review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    room_type: Mapped[str | None] = mapped_column(String, nullable=True)
    length_of_stay: Mapped[str | None] = mapped_column(String, nullable=True)

    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    # Denormalized sentiment, computed once at scrape/seed time by common.topics.
    sentiment: Mapped[str] = mapped_column(String, nullable=False, default="neutral")
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    property: Mapped["Property"] = relationship(back_populates="reviews")
    topics: Mapped[list["ReviewTopic"]] = relationship(
        back_populates="review", cascade="all, delete-orphan"
    )


class ReviewTopic(Base):
    __tablename__ = "review_topics"
    __table_args__ = (
        Index("ix_review_topics_topic", "topic"),
        UniqueConstraint("review_id", "topic", name="uq_review_topic"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), nullable=False)
    topic: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    matched_phrases: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    review: Mapped["Review"] = relationship(back_populates="topics")

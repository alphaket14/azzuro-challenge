"""Rule/keyword-based topic classification and sentiment derivation.

Methodology (documented here and in README.md):
  - Each review's full text is matched, case-insensitively, against phrase
    lists for 8 fixed operational topics (see topics.yaml). A review can
    match zero, one, or several topics.
  - "confidence" is a simple heuristic: matched_phrase_count / total phrases
    configured for that topic, capped at 1.0. It is NOT a calibrated
    probability - just a rough signal of how strongly a review touches a
    topic, useful for sorting/filtering, not for precise statistics.
  - Sentiment is derived primarily from the numeric rating (Booking.com's
    native 0-10 scale) and, when the rating is missing, falls back to a
    simple count of matched positive vs. negative keywords across all
    topics' lexicons.

Known limitations (see README.md for the full list):
  - No negation handling ("not dirty at all" still matches "dirty").
  - No sarcasm detection.
  - English-only keyword lists.
  - Multi-topic reviews are not weighted by which topic is "primary".
"""

import functools
import re
from dataclasses import dataclass, field

import yaml

from common.config import SENTIMENT_NEGATIVE_MAX, SENTIMENT_POSITIVE_MIN, TOPICS_CONFIG_PATH

TOPIC_NAMES = [
    "cleanliness",
    "check_in_experience",
    "staff_behaviour",
    "noise",
    "facilities",
    "location",
    "room_condition",
    "value_for_money",
]


@dataclass
class TopicMatch:
    topic: str
    confidence: float
    matched_phrases: list[str] = field(default_factory=list)
    positive_hits: int = 0
    negative_hits: int = 0


@functools.lru_cache(maxsize=1)
def _load_topic_config() -> dict:
    with open(TOPICS_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _phrase_pattern(phrase: str) -> re.Pattern:
    # Word-boundary-ish match that still works for multi-word phrases.
    escaped = re.escape(phrase.strip())
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", re.IGNORECASE)


@functools.lru_cache(maxsize=1)
def _compiled_patterns() -> dict[str, dict[str, list[tuple[str, re.Pattern]]]]:
    config = _load_topic_config()
    compiled: dict[str, dict[str, list[tuple[str, re.Pattern]]]] = {}
    for topic, lexicon in config.items():
        compiled[topic] = {
            "positive": [(p, _phrase_pattern(p)) for p in lexicon.get("positive_keywords", [])],
            "negative": [(p, _phrase_pattern(p)) for p in lexicon.get("negative_keywords", [])],
        }
    return compiled


def classify_review(text: str) -> list[TopicMatch]:
    """Return the topics a review's text matches, with a confidence score."""
    if not text:
        return []

    matches: list[TopicMatch] = []
    for topic, buckets in _compiled_patterns().items():
        matched_phrases: list[str] = []
        positive_hits = 0
        negative_hits = 0

        for phrase, pattern in buckets["positive"]:
            if pattern.search(text):
                matched_phrases.append(phrase)
                positive_hits += 1
        for phrase, pattern in buckets["negative"]:
            if pattern.search(text):
                matched_phrases.append(phrase)
                negative_hits += 1

        total_hits = positive_hits + negative_hits
        if total_hits == 0:
            continue

        total_keywords = len(buckets["positive"]) + len(buckets["negative"])
        confidence = min(1.0, total_hits / max(1, total_keywords))

        matches.append(
            TopicMatch(
                topic=topic,
                confidence=round(confidence, 3),
                matched_phrases=matched_phrases,
                positive_hits=positive_hits,
                negative_hits=negative_hits,
            )
        )

    return matches


def _keyword_polarity_score(text: str) -> int:
    """Net count of positive vs negative keyword hits across all topics."""
    score = 0
    for buckets in _compiled_patterns().values():
        for _, pattern in buckets["positive"]:
            if pattern.search(text):
                score += 1
        for _, pattern in buckets["negative"]:
            if pattern.search(text):
                score -= 1
    return score


def derive_sentiment(rating_raw: float | None, text: str) -> tuple[str, float]:
    """Return (label, score) where label is positive/neutral/negative and
    score is roughly in [-1.0, 1.0] for transparency/debugging."""
    if rating_raw is not None:
        if rating_raw >= SENTIMENT_POSITIVE_MIN:
            label = "positive"
        elif rating_raw <= SENTIMENT_NEGATIVE_MAX:
            label = "negative"
        else:
            label = "neutral"
        # Normalize 0-10 rating to a -1..1 score, centered at 5.
        score = round((rating_raw - 5.0) / 5.0, 3)
        return label, max(-1.0, min(1.0, score))

    # No rating available - fall back entirely to keyword polarity.
    polarity = _keyword_polarity_score(text)
    if polarity > 0:
        return "positive", min(1.0, polarity / 5)
    if polarity < 0:
        return "negative", max(-1.0, polarity / 5)
    return "neutral", 0.0

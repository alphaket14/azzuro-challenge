from common.topics import classify_review, derive_sentiment


def test_classify_review_detects_cleanliness_complaint():
    matches = classify_review("The room was dirty and the bathroom smelled.")
    topics = {m.topic for m in matches}
    assert "cleanliness" in topics


def test_classify_review_detects_multiple_topics():
    matches = classify_review("Staff was rude and the room was very noisy all night.")
    topics = {m.topic for m in matches}
    assert "staff_behaviour" in topics
    assert "noise" in topics


def test_classify_review_no_match_returns_empty():
    assert classify_review("Had a nice time overall.") == []


def test_derive_sentiment_uses_rating_when_present():
    label, score = derive_sentiment(9.0, "anything")
    assert label == "positive"
    assert score > 0

    label, score = derive_sentiment(3.0, "anything")
    assert label == "negative"
    assert score < 0


def test_derive_sentiment_falls_back_to_keywords_when_rating_missing():
    label, _ = derive_sentiment(None, "The room was dirty and outdated.")
    assert label == "negative"

    label, _ = derive_sentiment(None, "Clean room, great location.")
    assert label == "positive"

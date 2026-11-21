# Architecture overview

```
Booking.com property pages
        │
        │  Playwright (headless Chromium) + BeautifulSoup
        ▼
┌─────────────────┐
│  scraper/        │  navigates each property, paginates reviews,
│                  │  parses cards defensively, dedupes by content hash,
│                  │  classifies topics + sentiment (common/topics.py)
└────────┬─────────┘
         │ writes
         ▼
┌─────────────────┐
│  SQLite (data/   │  properties / reviews / review_topics
│  azzurro.db)     │  shared schema: common/models.py
└────────┬─────────┘
         │ reads (SQLAlchemy)
         ▼
┌─────────────────┐
│  backend/        │  FastAPI REST API: reviews, weekly/property summary,
│  (FastAPI)       │  topic insights, trends
└────────┬─────────┘
         │ fetch() over HTTP (JSON)
         ▼
┌─────────────────┐
│  frontend/       │  Next.js + React + Tailwind dashboard for
│  (Next.js)       │  non-technical ops staff
└─────────────────┘
```

## Why this split

- **scraper and backend share one Python package (`common/`)** for the DB
  schema, the dedup hash function, the properties list, and the topic
  classifier. This avoids re-implementing the same schema/logic in two
  places and guarantees the scraper's live-collection path and the
  `scripts/seed_db.py` demo-seeding path produce identical data shapes.
- **SQLite** is sufficient for 4 properties and a trial-task scale, requires
  no separate server, and is trivially portable (`data/azzurro.db`). WAL
  mode is enabled so the scraper (writer) and backend (reader) can both use
  the file without lock contention.
- **FastAPI** gives typed request/response validation (Pydantic) and
  auto-generated OpenAPI docs at `/docs`, useful both for frontend
  development and for a reviewer to inspect the API directly.
- **Next.js + Tailwind + Recharts** is a fast way to build a clean,
  responsive dashboard; Recharts covers every chart type needed (bar chart
  for property breakdown, bar chart for topic %, stacked area for trends)
  with one dependency.

## Data flow for a "live" run vs. a demo run

- **Live**: `python -m scraper.run` → Playwright hits the real Booking.com
  pages → parses/classifies/dedupes → writes directly into
  `data/azzurro.db` (and optionally exports to `data/sample_reviews.json`
  via `--export-json`).
- **Demo / grading** (no live scraping required): `data/sample_reviews.json`
  (committed) → `scripts/seed_db.py` → `data/azzurro.db`, using the exact
  same hashing/classification code as the live path.

Both paths converge on the same SQLite schema, so the backend and frontend
behave identically regardless of which path populated the data.

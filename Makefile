.PHONY: install seed scrape backend frontend dev test

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r backend/requirements.txt -r scraper/requirements.txt
	. .venv/bin/activate && playwright install chromium
	cd frontend && npm install

seed:
	. .venv/bin/activate && python scripts/seed_db.py --reset

scrape:
	. .venv/bin/activate && python -m scraper.run --properties all --max-pages 20 --export-json data/sample_reviews.json

backend:
	. .venv/bin/activate && uvicorn backend.app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	. .venv/bin/activate && python -m pytest -q

dev:
	@echo "Run 'make backend' and 'make frontend' in two separate terminals."

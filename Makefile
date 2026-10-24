bootstrap:
	uv sync --locked
	npm ci --ignore-scripts
	uv run python -m scripts.dev init

db:
	uv run python -m scripts.dev db

api:
	uv run python -m scripts.dev api

web:
	uv run python -m scripts.dev web

test:
	uv run python -m scripts.dev test

browser:
	uv run python -m scripts.dev browser

stop:
	uv run python -m scripts.dev stop

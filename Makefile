dev-install:
	python3.12 -m venv .venv && \
	source .venv/bin/activate && \
	pip install poetry keyring && \
	poetry install --no-root && \
	source .venv/bin/activate

.PHONY: test lint format

test:
	python -m pytest tests/ -v

lint:
	ruff check src/ tests/
	pyright

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

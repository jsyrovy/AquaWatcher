.DEFAULT:
	help

help:
	@echo "I don't know what you want me to do."

download:
	uv run --group downloader --no-dev --no-group publisher downloader.py

publish:
	uv run --group publisher --no-dev --no-group downloader downloader.py

mypy:
	uv run --dev -m mypy --ignore-missing-imports .

lint:
	uvx ruff check

lint-fix:
	uvx ruff check --fix

format:
	uvx ruff format

before-commit:
	make format
	make lint
	make mypy

ipython:
	uv run --dev --group downloader --group publisher python -c "import IPython;IPython.terminal.ipapp.launch_new_instance();"

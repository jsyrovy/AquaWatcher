PYTHON=venv/bin/python3

.DEFAULT:
	help

help:
	@echo "I don't know what you want me to do."

init:
	python3 -m venv venv
	${PYTHON} -m pip install -r downloader_requirements.txt
	${PYTHON} -m pip install -r publisher_requirements.txt

init-dev: init
	${PYTHON} -m pip install -r dev_requirements.txt

download:
	${PYTHON} downloader.py

publish:
	${PYTHON} publisher.py

mypy:
	${PYTHON} -m mypy --ignore-missing-imports .

flake8:
	${PYTHON} -m flake8 .

black:
	${PYTHON} -m black .

before-commit:
	make black
	make mypy
	make flake8

ipython:
	${PYTHON} -c "import IPython;IPython.terminal.ipapp.launch_new_instance();"

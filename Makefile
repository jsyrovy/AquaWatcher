PYTHON=venv/bin/python3

.DEFAULT:
	help

help:
	@echo "make help"
	@echo "  show help"
	@echo "make init"
	@echo "  create venv and install requirements"
	@echo "make download"
	@echo "  run downloader"
	@echo "make publish"
	@echo "  run publisher"
	@echo "make publish-after-covid"
	@echo "  run publisher for data after first lockdown"

init:
	python3 -m venv venv
	${PYTHON} -m pip install -r downloader_requirements.txt
	${PYTHON} -m pip install -r publisher_requirements.txt

download:
	${PYTHON} downloader.py

publish:
	${PYTHON} publisher.py

publish-after-covid:
	${PYTHON} publisher.py 2020-05-25 after_covid.html

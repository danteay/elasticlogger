lint:
	pylint ./elasticlogger
.PHONY: lint

fmt:
	black ./elasticlogger
.PHONY: fmt

install:
	pip install -r requirements.txt
.PHONY: install

build:
	rm -rf build dist *.egg-info *.eggs
	python3 setup.py sdist bdist_wheel
.PHONY: build

build-docs:
	sphinx-apidoc -o ./docs ./elasticlogger
.PHONY: build-docs

build-docs-html: build-docs
	make -C docs html
.PHONY: build-docs-html

venv:
	virtualenv venv --python=python3.7
.PHONY: venv

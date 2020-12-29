cc_json = "$(shell radon cc --min C src --ignore sdk --json)"
mi_json = "$(shell radon mi --min B src --json)"

lint:
	pylint ./elasticlogger
.PHONY: lint

fmt:
	yapf elasticlogger -r -i -vv
.PHONY: fmt

install:
	pip install yapf pylint radon
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

copy-docs: build-docs-html
	@rm -rf ../elasticlogger-docs/public && cp -r ./docs/_build/html ../elasticlogger-docs/public
.PHONY: copy-docs

venv:
	virtualenv venv --python=python3.8
.PHONY: venv

complexity:
	@echo "Complexity check..."

ifneq ($(cc_json), "{}")
	@echo
	@echo "Complexity issues"
	@echo "-----------------"
	@echo $(cc_json)
endif

ifneq ($(mi_json), "{}")
	@echo
	@echo "Maintainability issues"
	@echo "----------------------"
	@echo $(mi_json)
endif

ifneq ($(cc_json), "{}")
	@echo
	exit 1
else
ifneq ($(mi_json), "{}")
	@echo
	exit 1
endif
endif

	@echo "OK"
.PHONY: complexity


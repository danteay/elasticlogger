cc_json = "$(shell radon cc --min C src --ignore sdk --json)"
mi_json = "$(shell radon mi --min B src --json)"

help: ## Display this help screen.
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

lint: ## Style code linting
	@pylint ./elasticlogger

fmt: ## Format project code
	@yapf elasticlogger -r -i -vv

test: ## Run unit testings.
	@python -m unittest discover -s tests -v

install: ## Install project dependencies
	pip install yapf pylint radon
	pip install -r requirements.txt

build: ## Build project to be uploaded
	rm -rf build dist *.egg-info *.eggs
	python3 setup.py sdist bdist_wheel

build-docs: ## Compile Sphinx documentation
	sphinx-apidoc -o ./docs ./elasticlogger

build-docs-html: build-docs ## Create HTML docs from Sphinx
	make -C docs html

copy-docs: build-docs-html ## Copy HTML docs to the documentation repo
	@rm -rf ../elasticlogger-docs/public && cp -r ./docs/_build/html ../elasticlogger-docs/public

venv: ## Create virtual environment
	virtualenv venv --python=python3.8

complexity: ## Check project maintainability and complexity
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


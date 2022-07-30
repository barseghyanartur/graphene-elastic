.PHONY: help clean

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@echo "clean | Remove all build, test, coverage and Python artifacts"
	@echo "clean-build | Remove build artifacts"
	@echo "clean-pyc | Remove Python file artifacts"
	@echo "clean-test | Remove test and coverage artifacts"
	@echo "run | Run the project in Docker"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf **/*.egg-info
	rm -rf static/CACHE

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -rf .pytest_cache; \
	rm -rf .ipython/profile_default; \
	rm -rf htmlcov; \
	rm -rf build; \
	rm -f .coverage; \
	rm -f coverage.xml; \
	rm -f junit.xml; \
	rm -rf .hypothesis; \
	find . -name '*.py,cover' -exec rm -f {} +

pip-compile:
	pip-compile requirements/code_style.in
	pip-compile requirements/common.in
	pip-compile requirements/debug.in
	pip-compile requirements/dev.in
	pip-compile requirements/django.in
	pip-compile requirements/docs.in
	pip-compile requirements/documentation.in
	pip-compile requirements/elastic_6x.in
	pip-compile requirements/elastic_7x.in
	pip-compile requirements/fastapi.in
	pip-compile requirements/flask.in
	pip-compile requirements/responder.in
	pip-compile requirements/test.in
	pip-compile requirements/testing_6x.in
	pip-compile requirements/testing_7x.in

install-pip-tools:
	pip install -r requirements/build.in

install: install-pip-tools pip-compile
	pip install -r requirements/dev.txt

black:
	black .

isort:
	isort . --overwrite-in-place

test:
	./runtests.py -vvv -s

docker-run:
	docker-compose up --abort-on-container-exit

docker-test:
	docker-compose -f test.yml up --abort-on-container-exit
	docker-compose -f test_6x.yml up --abort-on-container-exit

release:
	python setup.py register
	python setup.py sdist bdist_wheel
	twine upload dist/* --verbose

build-docs:
	sphinx-build -n -a -b html docs builddocs
	cd builddocs && zip -r ../builddocs.zip . -x ".*" && cd ..

rebuild-docs:
	sphinx-apidoc graphene-elastic --full -o docs -H 'graphene-elastic' -A 'Artur Barseghyan <artur.barseghyan@gmail.com>' -f -d 20

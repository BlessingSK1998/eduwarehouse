PY=.venv/bin/python
DBT=cd dbt && ../.venv/bin/dbt

setup:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && $(DBT) deps --profiles-dir .
test:
	$(PY) -m pytest -q tests
extract load:
	$(PY) -m pipeline.run $@
build:
	$(DBT) build --profiles-dir .
dashboard:
	$(PY) dashboard/build.py
all:
	$(PY) -m pipeline.run all && $(DBT) build --profiles-dir . && cd .. && $(PY) dashboard/build.py
.PHONY: setup test extract load build dashboard all

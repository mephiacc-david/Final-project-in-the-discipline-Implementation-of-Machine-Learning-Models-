PYTHON ?= python3
PORT ?= 8000

.PHONY: install prepare-data train run test lint format security quality-check docker-build docker-run

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

prepare-data:
	$(PYTHON) -m src.data.make_dataset

train:
	$(PYTHON) -m src.train.train_all

run:
	$(PYTHON) -m app.api

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m black .

security:
	$(PYTHON) -m bandit -c pyproject.toml -r app src
	XDG_CACHE_HOME=.cache $(PYTHON) -m pip_audit --local

quality-check:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .
	$(PYTHON) -m pytest
	$(PYTHON) -m bandit -c pyproject.toml -r app src
	XDG_CACHE_HOME=.cache $(PYTHON) -m pip_audit --local

docker-build:
	docker build -t credit-default-service:local .

docker-run:
	docker run --rm -e PORT=$(PORT) -p $(PORT):$(PORT) credit-default-service:local

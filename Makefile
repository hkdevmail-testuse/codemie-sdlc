.PHONY: help venv install lint test package clean run

APP_NAME := expense-tracker
DIST_DIR := dist
VENV_DIR := .venv
PY := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

help:
	@echo "Targets:"
	@echo "  venv      - Create virtualenv"
	@echo "  install   - Install prod deps"
	@echo "  lint      - Run ruff (if configured)"
	@echo "  test      - Run pytest"
	@echo "  package   - Build deployable artifact (zip)"
	@echo "  run       - Run flask app locally"
	@echo "  clean     - Remove venv/dist"

venv:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r src/requirements.txt

lint: install
	@$(PY) -m ruff --version >/dev/null 2>&1 && $(PY) -m ruff check src || echo "ruff not installed; skipping lint"

test: install
	@$(PY) -m pytest -q || (echo "No tests or tests failed" && exit 1)

package: install
	mkdir -p $(DIST_DIR)
	$(PY) scripts/build.py --out $(DIST_DIR)/$(APP_NAME).zip

run: install
	FLASK_APP=src/app.py $(PY) -m flask run

clean:
	rm -rf $(VENV_DIR) $(DIST_DIR) .pytest_cache .ruff_cache build
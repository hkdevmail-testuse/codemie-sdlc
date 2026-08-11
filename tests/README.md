# Automated Tests (PyTest)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # mac/linux
# .venv\\Scripts\\activate  # windows

pip install -r src/requirements.txt
pip install -r tests/requirements-test.txt
```

## Run

From repository root:

```bash
pytest -q
```

## Reports

```bash
pytest -q \
  --html=reports/pytest-report.html --self-contained-html \
  --json-report --json-report-file=reports/pytest-report.json
```

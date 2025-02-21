test-unit:
	uv run --frozen pytest -s --cov=domprob/ test/unit --cov-report=html --cov-report=term --cov-report=xml --junitxml=junit.xml -o junit_family=legacy

test-functional:
	uv run --frozen pytest test/functional

test-integration:
	uv run --frozen pytest test/integration

.PHONY: test
test:
	uv run --frozen pytest -s test/

doctest:
	uv run --frozen pytest domprob/ docs/ --doctest-modules

test-all:
	uv run --frozen pytest -s domprob/ docs/ test/ --doctest-modules

.PHONY: docs
docs:
	uv run sphinx-build -M html docs/ docs/_build/

autodocs:
	uv run sphinx-autobuild docs/ docs/_build/

mypy:
	uv run mypy domprob/ --check-untyped-defs --show-error-context

pylint:
	uv run pylint domprob/

black:
	uv run black domprob/ test/ --line-length=79

black-check:
	uv run black domprob/ test/ --line-length=79 --check

isort:
	uv run isort domprob/ test/

isort-check:
	uv run isort domprob/ test/ --check

lint: black-check isort-check mypy pylint

lock:
	uv lock --upgrade
	uv sync --no-editable
	uv export --frozen --format=requirements-txt --no-emit-project --output-file=docs/requirements.txt

test-unit:
	uv run --frozen pytest --cov=domprob/ test/unit --cov-report=html --cov-report=term --cov-report=xml

test-functional:
	uv run --frozen pytest test/functional

.PHONY: test
test:
	uv run --frozen pytest -s test/

doctest:
	uv run --frozen pytest domprob/ docs/ --doctest-modules

test-all:
	uv run --frozen pytest domprob/ docs/ test/ --doctest-modules

.PHONY: docs
docs:
	uv run sphinx-build -M html docs/ docs/_build/

autodocs:
	uv run sphinx-autobuild docs/ docs/_build/

mypy:
	uv run mypy domprob/

pylint:
	uv run pylint domprob/

black:
	uv run black domprob/ --line-length=79

black-check:
	uv run black domprob/ --line-length=79 --check

lint: black-check mypy pylint

lock:
	uv lock
	uv sync --no-editable
	uv export --frozen --format=requirements-txt --no-emit-project --output-file=docs/requirements.txt

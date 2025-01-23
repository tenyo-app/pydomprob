test-unit:
	uv run --frozen pytest -s --cov=domprob/ test/unit --cov-report=html --cov-report=term

test-functional:
	uv run --frozen pytest -s test/functional

.PHONY: test
test:
	uv run --frozen pytest -s test/

doctest:
	uv run --frozen pytest -s domprob/ docs/ --doctest-modules

test-all:
	uv run --frozen pytest -s domprob/ docs/ test/ --doctest-modules

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

lint: mypy pylint black-check

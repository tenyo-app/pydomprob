test:
	uv run --frozen pytest -s test/

test-unit:
	uv run --frozen pytest -s --cov=domprob/ test/unit --cov-report=html --cov-report=term

test-functional:
	uv run --frozen pytest -s test/functional

doctest:
	uv run --frozen pytest domprob/ docs/ -s --doctest-modules

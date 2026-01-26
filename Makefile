sources = src/fastdistill tests

.PHONY: format
format:
	ruff --version
	ruff check --fix $(sources)
	ruff format $(sources)

.PHONY: lint
lint:
	ruff --version
	ruff check $(sources)
	ruff format --check $(sources)

.PHONY: unit-tests
unit-tests:
	./scripts/run_unit_tests.sh

.PHONY: integration-tests
integration-tests:
	pytest tests/integration

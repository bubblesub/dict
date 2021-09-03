test:
	pytest --cov=dict --cov-report term-missing

lint:
	pre-commit run -a

clean:
	rm .coverage
	rm -rf .mypy_cache
	rm -rf .pytest_cache

.PHONY: test lint clean

lint:
	pylint ssg/ tests/
	flake8 ssg/ tests/ --max-complexity=10

check:
	mypy ssg/ tests/ --strict

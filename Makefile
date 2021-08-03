lint:
	pylint ssg/ tests/
	flake8 ssg/ tests/ --max-complexity=3

lint:
	pylint sausage/ tests/
	flake8 sausage/ tests/ --max-complexity=10

check:
	mypy sausage/ tests/ --strict

dist:
	python setup.py sdist bdist_wheel

.PHONY:	lint check dist

test: flake8 mypy pytest black_format_check

coverage:
	pytest --cov .

format:
	black src/qmake2cmake/

black_format_check:
	black src/qmake2cmake/ --check

flake8:
	flake8 src/qmake2cmake/ --ignore=E501,E266,E203,W503,F541

pytest:
	pytest

mypy:
	mypy

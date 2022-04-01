SOURCES = condition_simplifier_cache.py condition_simplifier.py helper.py pro2cmake.py pro_conversion_rate.py qmake_parser.py run_pro2cmake.py special_case_helper.py

test: flake8 mypy pytest black_format_check

coverage:
	pytest --cov .

format:
	black $(SOURCES) --line-length 100

black_format_check:
	black $(SOURCES) --line-length 100 --check

flake8:
	flake8 $(SOURCES) --ignore=E501,E266,E203,W503,F541

pytest:
	pytest

mypy:
	mypy $(SOURCES)

build:
	python3 -m pip install -e '.'

build-test:
	python3 -m pip install -e '.[test]'

clean:
	rm -rf build .pytest_cache dist subtensorapi.egg-info

test-package:
	python3 -m unittest discover -s tests
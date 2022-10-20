build:
	python3 -m pip install -e '.'

build-dev:
	python3 -m pip install -e '.[dev]'

clean:
	rm -rf build .pytest_cache dist subtensorapi.egg-info

test-package:
	python3 -m unittest discover -s subtensor-api/tests
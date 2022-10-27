VERSION := $(shell cat VERSION)

# Cleaning the build directories between wheels is important to ensure that the
# binaries are only distributed in one wheel for the correct platform.
dist: .PHONY
	@echo "Building subtensor-api-v$(VERSION)"
	$(MAKE) clean_dist
	$(MAKE) clean
	cd ../js && $(MAKE) build
	$(MAKE) copy
	$(MAKE) dist-macos
	$(MAKE) clean
	$(MAKE) dist-linux

dist-macos: .PHONY
	BT_BUILD_TARGET=darwin python3 -m build --wheel && \
		mv dist/subtensorapi-$(VERSION)-py3-none-any.whl dist/subtensorapi-$(VERSION)-py3-none-macosx_10_15_universal2.whl
	
dist-linux: .PHONY
	BT_BUILD_TARGET=linux python3 -m build --wheel && \
		mv dist/subtensorapi-$(VERSION)-py3-none-any.whl dist/subtensorapi-$(VERSION)-py3-none-manylinux_2_17_x86_64.whl

copy: .PHONY
	@echo "Copying binaries to subtensor-api"
	cp -r ../js/subtensor-node-api-* ./src/subtensorapi/bin/

install:
	python3 -m pip install -e '.'

install-test:
	python3 -m pip install -e '.[test]'

clean:
	rm -rf build .pytest_cache subtensorapi.egg-info

clean_dist:
	rm -rf dist

test-package:
	python3 -m unittest discover -s tests

.PHONY:
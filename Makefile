.PHONY: dist

clean:
	rm -rf build/ dist/ qanary_helpers.egg-info/ __pycache__/ */__pycache__/ .pytest_cache/
	rm -f *.pyc */*.pyc

install:
	python3 setup.py sdist bdist_wheel

test:
	pytest

upload:
	twine upload dist/*


clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	rm -rf .cache

dist-clean: clean
	rm -rf *.egg-info/

test-clean: clean
	rm .coverage
	rm -rf htmlcov/

html-cov:
	py.test --cov=rematch
	coverage html
	cd htmlcov && python -m http.server

term-cov:
	py.test --verbose --cov-report term --cov=rematch tests

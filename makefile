.PHONY: run clean
test:
	# run all tests in test folder
	.dev-venv/bin/python3 -m unittest discover -v
setup:
	# setup script to run
	# make setup
	pip install -r dev-requirements.txt
clean:
	# clean pycache
	# make clean
	rm -rf __pycache__
	rm -rf venv
	rm -rf .dev-venv
.dev-venv/bin/activate: dev-requirements.txt
	# build venv
	# update venv if requirements is changed
	python3 -m venv .dev-venv
	./.dev-venv/bin/pip install -r dev-requirements.txt

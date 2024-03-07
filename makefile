.PHONY: run clean local
test:
	# run all tests in test folder
	./.dev-venv/bin/python3 -m unittest discover -v
setup:
	# setup script to run
	# make setup
	pip install -r requirements.txt
clean:
	# clean pycache
	# make clean
	rm -rf __pycache__
	rm -rf venv
	rm -rf .dev-venv
.venv/bin/activate: requirements.txt
	# build venv
	# update venv if requirements is changed
	python3 -m venv .venv
	./.venv/bin/pip install -r requirements.txt
local:
	# run flask server locally
	# in debug mode
	. .venv/bin/activate
	export FLASK_DEBUG=1
	flask run

install:
	@test -d env || python3.10 -m venv env
	@. env/bin/activate && pip install -r requirements.txt

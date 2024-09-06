PROJECT_NAME = polar-vanatage-v-gps
VENV_PATH = ~/.venv/$(PROJECT_NAME)

all: venv install jupyter docker

venv:
	@python3 -m venv $(VENV_PATH)

install: venv
	@source $(VENV_PATH)/bin/activate && \
	pip install --disable-pip-version-check -q -r requirements.txt

jupyter:
	@source $(VENV_PATH)/bin/activate && \
	python3 -m ipykernel install \
	--user --name=$(PROJECT_NAME) \
	--display-name "$(PROJECT_NAME)"

docker:
	@open -a Docker
	@while ! docker info > /dev/null 2>&1; do \
		sleep 1; \
	done
	@docker stop $$(docker ps -a -q)
	@docker compose up --build -d
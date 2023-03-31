build:
	docker-compose build

rebuild:
	docker-compose build --no-cache

up:
	docker-compose up -d

down:
	docker-compose down


build_python_env:
	conda env create -f environment.yml && conda activate web_spider && conda install ipykernel -y && \
	python -m ipykernel install --user --name web_spider --display-name "Python (web_spider)"


run:
	source .secrets && cd career_hub && python main.py


update-env:
	conda env update --file environment.yml


bash:
	docker-compose exec scrapy bash
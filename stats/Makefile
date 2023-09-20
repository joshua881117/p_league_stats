	
create-mysql-volume:
	docker volume create mysql

create-network:
	docker network create my_network

deploy-mysql:
	docker-compose -f mysql.yml mysql

deploy-rabbitmq:
	docker-compose -f rabbitmq.yml rabbitmq

create-game-task:
	pipenv run python stats/execute.py game 2020-21 1 48

create-year-task:
	pipenv run python stats/execute.py year 2020-21 2022-23

execute-game-task:
	pipenv run celery -A stats.tasks.worker worker --loglevel=info --concurrency=1  --hostname=%h -Q game

execute-year-task:
	pipenv run celery -A stats.tasks.worker worker --loglevel=info --concurrency=1  --hostname=%h -Q year
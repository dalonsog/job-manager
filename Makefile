dev:
	docker compose build
	docker compose up -d
	docker exec -it app python jobmanager/scripts/init_db.py

init-db:
	docker exec -it app python jobmanager/scripts/init_db.py

up:
	docker compose up -d

log:
	docker compose logs -f -t

run:
	docker compose build
	docker compose up -d

down:
	docker compose down

kill:
	docker compose kill

local:
	fastapi dev jobmanager/main.py

local-test:
	pytest test -v
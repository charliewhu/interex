test:
	pytest -s

testp:
	pytest -sn auto

dev:
	ENV=dev docker compose up

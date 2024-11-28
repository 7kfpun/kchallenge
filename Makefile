help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

amd64:
	export DOCKER_DEFAULT_PLATFORM=linux/amd64

up:  ## Docker up
	docker-compose -f docker-compose.yml up

upd:  ## Docker deamon up
	docker-compose -f docker-compose.yml up -d

upddev:  ## Docker deamon up with dev environment
	docker-compose -f docker-compose.yml -f docker-compose.devenv.yml up -d

build:  ## Build
	docker-compose -f docker-compose.yml up --build

proto:  ## Generate proto
	python3 -m grpc_tools.protoc -I app/grpc_services/proto --python_out=app/grpc_services/proto --grpc_python_out=app/grpc_services/proto app/grpc_services/proto/marvel.proto
	sed -i '' 's/import marvel_pb2 as/import app.grpc_services.proto.marvel_pb2 as/' app/grpc_services/proto/marvel_pb2_grpc.py
	# sed -i '' 's/import marvel_pb2 as/import app.grpc_services.proto.marvel_pb2 as/' app/grpc_services/proto/marvel_pb2.py

lint:  ## Lint
	autoflake --exclude venv --in-place --remove-all-unused-imports --remove-duplicate-keys --remove-unused-variables **/*.py
	black . --exclude=venv

test:  ## Test
	python3 -m unittest discover -s tests

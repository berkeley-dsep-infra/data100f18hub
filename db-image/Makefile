IMAGE=berkeleydsep/data100-db-pull
VERSION=v4

build:
	docker build -t $(IMAGE):$(VERSION) .

run:
	docker run --rm \
		-e DB_URL="https://s3.amazonaws.com/simon-mo-dev-public/ds100/taxi_2018.sqlite" \
		-e DB_PATH='/var/tmp/foo' \
		-v /var/tmp:/var/tmp \
		$(IMAGE):$(VERSION) 

push:
	docker push $(IMAGE):$(VERSION)

release: build push

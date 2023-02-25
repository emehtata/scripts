IMAGE=ruuvi2mqtt

build:
	docker build . -t $(IMAGE)

run:
	docker run --rm --name ruuvi2mqtt $(IMAGE)

run_bash:
	docker run --rm -it --entrypoint bash $(IMAGE)

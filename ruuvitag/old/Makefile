#IMAGE=ruuvi2mqtt
IMAGE=localhost:5000/ruuvi2mqtt-rpi3-arm7:latest
NAME=ruuvi2mqtt

build:
	docker build . -t $(IMAGE)

run:
	docker run -d --name $(NAME) --privileged --network=host --restart=unless-stopped -v $(PWD):/app $(IMAGE)

stop:
	docker stop $(NAME)

run_bash:
	docker run --rm -it --entrypoint bash $(IMAGE)

rm: stop
	docker rm $(NAME)


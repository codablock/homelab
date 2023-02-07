#!/bin/sh

set -e

docker build -t docker-registry.homelab.codablock.de/shelly-mqtt shelly-mqtt-image
docker push docker-registry.homelab.codablock.de/shelly-mqtt

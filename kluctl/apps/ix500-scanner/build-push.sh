#!/bin/sh

set -e

docker build --platform linux/amd64 -t docker-registry.homelab.codablock.de/ix500-scanner ix500-scanner-image
docker push docker-registry.homelab.codablock.de/ix500-scanner

docker build --platform linux/amd64 -t docker-registry.homelab.codablock.de/scan2pdf scan2pdf-image
docker push docker-registry.homelab.codablock.de/scan2pdf

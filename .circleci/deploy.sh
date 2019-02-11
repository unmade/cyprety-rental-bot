#!/usr/bin/env bash

CONTAINER_NAME="cyrentbot"


mkdir -p ~/cyprety-rental-bot

echo "Pulling image from Dockerhub"
docker pull fdooch/cyrentbot:$2

echo "Stopping previously running container"
docker ps -q --filter "name=${CONTAINER_NAME}" | grep -q . && docker stop ${CONTAINER_NAME}

echo "Starting new container"
docker run \
    -d \
    --rm \
    --env TELEGRAM_BOT_TOKEN=$1 \
    --env SENTRY_RELEASE_VERSION=$2 \
    --volume ~/cyprety-rental-bot/sqlite.db:/cyprety-rental-bot/sqlite.db \
    --name ${CONTAINER_NAME} \
    fdooch/cyrentbot:$2

echo "docker ps"
docker ps

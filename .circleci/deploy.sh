#!/usr/bin/env bash

CONTAINER_NAME="cyrentbot"

TELEGRAM_BOT_TOKEN=$1
TAG=$2
SENTRY_DSN=$3
SENTRY_RELEASE_VERSION=$4

mkdir -p ~/cyprety-rental-bot

echo "Pulling image from Dockerhub"
docker pull fdooch/cyrentbot:${TAG}

echo "Stopping previously running container"
docker ps -q --filter "name=${CONTAINER_NAME}" | grep -q . && docker stop ${CONTAINER_NAME}

echo "Starting new container"
docker run \
    -d \
    --rm \
    --env TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN} \
    --env SENTRY_DSN=${SENTRY_DSN} \
    --env SENTRY_RELEASE_VERSION=${SENTRY_RELEASE_VERSION} \
    --cpus=".5" \
    --memory="512m" \
    --memory-swap="512m" \
    --volume ~/cyprety-rental-bot/sqlite.db:/cyprety-rental-bot/sqlite.db \
    --name ${CONTAINER_NAME} \
    fdooch/cyrentbot:${TAG}

echo "docker ps"
docker ps

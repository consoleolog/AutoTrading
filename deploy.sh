#!/bin/bash

IMAGE_NAME=autotrading
CONTAINER_NAME=server

EXIST_BLUE=$(sudo docker-compose -p $CONTAINER_NAME-blue -f docker-compose.blue.yaml ps | grep Up)
IMAGE_ID=$(sudo docker images -q $IMAGE_NAME)

if [ -z "$EXIST_BLUE" ]; then
  echo "blue up"
  sudo docker-compose -p $CONTAINER_NAME-blue -f docker-compose.blue.yaml up -d --build
  BEFORE_COMPOSE_COLOR="green"
  AFTER_COMPOSE_COLOR="blue"
else
  echo "green up"
  sudo docker-compose -p $CONTAINER_NAME-green -f docker-compose.green.yaml up -d --build
  BEFORE_COMPOSE_COLOR="blue"
  AFTER_COMPOSE_COLOR="green"
fi

sleep 10

EXIST_AFTER=$(sudo docker-compose -p "$CONTAINER_NAME-$AFTER_COMPOSE_COLOR" -f docker-compose.${AFTER_COMPOSE_COLOR}.yaml ps | grep Up)
if [ -n "$EXIST_AFTER" ]; then
  sudo docker-compose -p "$CONTAINER_NAME-$BEFORE_COMPOSE_COLOR" -f docker-compose.${BEFORE_COMPOSE_COLOR}.yaml down
  echo "$BEFORE_COMPOSE_COLOR down"
  sudo docker rmi "$IMAGE_ID"
fi
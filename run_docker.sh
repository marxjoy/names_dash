#!/usr/bin/env bash

echo killing old docker processes
docker-compose rm -fs

echo building docker containers
docker-compose up --build --force-recreate -d

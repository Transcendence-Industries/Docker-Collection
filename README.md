# Docker Collection

## General setup

- Change the marked settings in the `docker-compose.yml` file.
- Copy the `stack.env.sample` and change all neccessary settings.
- Use `docker compose up -d` to deploy the container.

## BluRay Sales

> Tool for checking availabilities and sales of Blu-Rays at multiple shops.

## Car Store

> Tool for checking inventories of car manufacturers.

## Immich Albums

> Organizer for matching directories to albums on Immich.

## Music Tags

> Organizer for setting metdata of MP3 files.

## Node Website

> Simple server for hosting Node.JS based websites.

- Additonal setup:
    - Use `docker volume create <VOLUME_NAME>` to create a docker volume with the previous coosen name.
    - Use `docker cp <SRC_DIR> <CONTAINER_NAME>:/app` to copy the website's source files to the previous deployed docker container.

## Python Scheduler

> Simple scheduler that runs scripts with given arguments.

- Additional setup:
    - Use `docker volume create <VOLUME_NAME>` to create a docker volume with the previous coosen name.
    - Create a `config.json` file for the desired configuration.
    - Use `docker cp <CONFIG_PATH> <CONTAINER_NAME>:/app` to copy the config file to the previous deployed docker container.

## RSS AI

> AI agent for prioritzing and summarizing articles from a FreshRSS feed.

## YouTube Music

> Tool for creating a hierarchy of music-channels on YouTube.

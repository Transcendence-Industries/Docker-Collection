# Docker Collection

## BluRay Sales

> Tool for checking availabilities and sales of Blu-Rays at multiple shops.

- Setup:
    - Change the marked settings in the `docker-compose.yml` file.
    - Copy the `stack.env.sample` and change all neccessary settings.
    - Use `docker compose up -d` to deploy the container.

## Car Store

> Tool for checking inventories of car manufacturers.

- Setup:
    - Change the marked settings in the `docker-compose.yml` file.
    - Copy the `stack.env.sample` and change all neccessary settings.
    - Use `docker compose up -d` to deploy the container.

## Immich Albums

> Organizer for matching directories to albums on Immich.

- Setup:
    - Change the marked settings in the `docker-compose.yml` file.
    - Copy the `stack.env.sample` and change all neccessary settings.
    - Use `docker compose up -d` to deploy the container.

## Music Tags

> Organizer for setting metdata of MP3 files.

- Setup:
    - Change the marked settings in the `docker-compose.yml` file.
    - Copy the `stack.env.sample` and change all neccessary settings.
    - Use `docker compose up -d` to deploy the container.

## Node Website

> Simple server for hosting Node.JS based websites.

- Setup:
    - Change the marked settings in the `docker-compose.yml` file.
    - Use `docker volume create <VOLUME_NAME>` to create a docker volume with the previous coosen name.
    - Use `docker compose up -d` to deploy the container.
    - Use `docker cp <SRC_DIR> <CONTAINER_NAME>:/app` to copy the website's source files to the previous deployed docker container.

## Python Scheduler

> Simple scheduler that runs scripts with given arguments.

- Setup:
    - Change the marked settings in the `docker-compose.yml` file.
    - Use `docker volume create <VOLUME_NAME>` to create a docker volume with the previous coosen name.
    - Use `docker compose up -d` to deploy the container.
    - Create a `config.json` file for the configuration.
    - Use `docker cp <CONFIG_PATH> <CONTAINER_NAME>:/app` to copy the config file to the previous deployed docker container.

## YouTube Music

> Tool for creating a hierarchy of music-channels on YouTube.

- Setup:
    - Change the marked settings in the `docker-compose.yml` file.
    - Copy the `stack.env.sample` and change all neccessary settings.
    - Use `docker compose up -d` to deploy the container.

# Docker Collection

## Flask Website

> Simple server for hosting Flask based websites.

- Setup:
    - Change the marked settings in the `docker-compose.yml` file.
    - Use `docker volume create <VOLUME_NAME>` to create a docker volume with the previous coosen name.
    - Use `docker compose up -d` to deploy the container.
    - Use `docker cp <SRC_DIR> <CONTAINER_NAME>:/app` to copy the website's source files to the previous deployed docker container.

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

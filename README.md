# Docker Collection

## Node Website

> Simple server for hosting Node.JS based websites.

- Setup:
    - Change the marked settings in the `docker-compose.yml` file.
    - Use `docker volume create <VOLUME_NAME>` to create a docker volume with the previous coosen name.
    - Use `docker compose up -d` to deploy the container.
    - Use `docker cp <SRC_DIR> <CONTAINER_NAME>:/app` to copy the website's source files to the previous deployed docker container.

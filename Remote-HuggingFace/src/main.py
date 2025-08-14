import os
import logging
import uvicorn

DEBUG = bool(os.environ["DEBUG"])
API_PORT = int(os.environ["API_PORT"])
CACHE_DIR = str(os.environ["CACHE_DIR"])

os.environ["HF_HOME"] = os.path.abspath(CACHE_DIR)


def main_entrypoint():
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
    uvicorn.run("api:app", host="0.0.0.0", port=API_PORT)


if __name__ == "__main__":
    main_entrypoint()

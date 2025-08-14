import os
import logging
import waitress

import feed

DEBUG = bool(os.environ["DEBUG"])
FEED_PORT = int(os.environ["FEED_PORT"])


def main_entrypoint():
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

    logging.info(f"Starting server on port {FEED_PORT}...")
    waitress.serve(feed.app, host="0.0.0.0", port=FEED_PORT)


if __name__ == "__main__":
    main_entrypoint()

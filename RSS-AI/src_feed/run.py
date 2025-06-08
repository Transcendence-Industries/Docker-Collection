import os
import logging
import waitress

import feed

FEED_PORT = int(os.environ["FEED_PORT"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info(f"Starting server on port {FEED_PORT}...")
    waitress.serve(feed.app, host="0.0.0.0", port=FEED_PORT)

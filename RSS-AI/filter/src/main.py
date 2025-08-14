import os
import logging

import filter

DEBUG = bool(os.environ["DEBUG"])


def main_entrypoint():
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
    filter.main_run()


if __name__ == "__main__":
    main_entrypoint()

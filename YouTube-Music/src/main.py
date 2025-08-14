import os
import logging
from streamlit.web import cli

DEBUG = bool(os.environ["DEBUG"])


def main_entrypoint():
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
    cli.main_run([
        "interface.py",
        "--server.port", "8501",
        "--browser.gatherUsageStats", "false"
    ])


if __name__ == "__main__":
    main_entrypoint()

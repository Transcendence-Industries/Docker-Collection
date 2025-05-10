import logging
from streamlit.web import cli

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli.main_run(["interface.py", "--server.port", "8501", "--browser.gatherUsageStats", "false"])

import os
import json
import logging
import subprocess
from datetime import datetime

DEBUG = bool(os.environ["DEBUG"])

LOG_PATH = "/data/logs"
SCRIPT_PATH = "/data/scripts"
CONFIG_FILE = "/data/config.json"


def send_email(title, conent):
    # TODO
    pass


def run_script(script, args):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_name = os.path.join(LOG_PATH, f"{script} - {timestamp}.log")
    logging.info(f"Starting execution of script '{script}'.")

    try:
        # Build working directory & args
        work_dir = os.path.join(SCRIPT_PATH, script)
        logging.debug(f"Executing in directory: {work_dir}")
        logging.debug(f"Executing with args: {args}")

        # Execute script
        process = subprocess.Popen(
            cwd=work_dir,
            args=args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True)

        # Capture output
        with open(log_name, "w") as log_file:
            for line in process.stdout:
                logging.debug(f"> {line}")
                log_file.write(line)

        # Wait for termination
        exit_code = process.wait()
        logging.info(
            f"Finished execution of script '{script}' with exit-code {exit_code}.")
    except Exception as e:
        exit_code = -1
        logging.warning(f"Error during execution of '{script}': {str(e)}")


def main_entrypoint():
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

    logging.info("Loading configuration from JSON file...")
    with open(CONFIG_FILE, "r") as file:
        data = json.load(file)

    logging.info(f"Starting scheduler for {len(data)} scripts.")
    for script in data:
        for run in data[script]:
            run_script(script, run["args"])

    logging.info("Completed scheduler.")


if __name__ == "__main__":
    main_entrypoint()

import os
import json
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

import scraper_tesla
from models import TeslaModelS, TeslaModel3

DATA_PATH = str(os.environ["DATA_PATH"])
PLAYWRIGHT_DRIVER = str(os.environ["PLAYWRIGHT_DRIVER"])
PLAYWRIGHT_RETRIES = int(os.environ["PLAYWRIGHT_RETRIES"])
PLAYWRIGHT_TIMEOUT = int(os.environ["PLAYWRIGHT_TIMEOUT"])

TESLA_FILE = "Tesla.json"


def init_scraper(instance):
    logging.info("Connecting scraper...")
    ua = UserAgent()
    user_agent = ua.chrome  # Universal: 'ua.random'

    try:
        browser = instance.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()
        logging.info("Connected scraper.")
        return browser, context
    except:
        logging.error("Failed to connect scraper!")
        return None, None


def shutdown_scraper(browser, context):
    logging.info("Shutting down scraper...")
    context.close()
    browser.close()
    logging.info("Scraper is shut down.")


def scrape_tesla(filter: TeslaModelS | TeslaModel3):
    request = str(filter)
    result = load_from_json(TESLA_FILE)
    result = check_request_json(result, request)

    if not result:
        with sync_playwright() as playwright:
            browser, context = init_scraper(playwright)

            if browser and context:
                curr_try = 1
                result = None

                while not result and curr_try <= PLAYWRIGHT_RETRIES:
                    try:
                        result = scraper_tesla.get_vehicles(context, filter)
                        save_to_json(TESLA_FILE, request, result)
                    except Exception as e:
                        logging.error(e)
                        logging.warning(
                            f"Failed to scrape Tesla for '{request}' ({curr_try}/{PLAYWRIGHT_RETRIES} tries)!")
                        result = None
                    curr_try += 1

                shutdown_scraper(browser, context)
            else:
                result = None
    else:
        logging.info(f"Loaded cached result for '{request}'.")

    # [ {"name": NAME, "link": LINK, "pictures": [PICTURE, ...], "location": LOCATION, "price": PRICE, "details": DETAILS}, ... ]
    return result


def load_from_json(file):
    path = os.path.join(DATA_PATH, file)

    try:
        logging.debug(f"Loading file {path}'...")
        with open(path, "r") as f:
            data = json.load(f)
        return data
    except:
        logging.warning(f"Failed to load file '{path}'!")
        return None


def save_to_json(file, request, result):
    path = os.path.join(DATA_PATH, file)
    new_data = {
        "time": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "request": request,
        "result": result
    }

    curr_data = load_from_json(file)
    if curr_data and len(curr_data) > 0:
        curr_data.append(new_data)
    else:
        curr_data = [new_data]

    try:
        logging.debug(f"Writing file {path}'...")
        with open(path, "w") as f:
            json.dump(curr_data, f, indent=4)
    except:
        logging.warning(f"Failed to write file '{path}'!")


def check_request_json(result, request):
    if result and len(result) > 0:
        for elem in result:
            if elem["request"] == request:
                return elem["result"]
    return None


def delete_json(file):
    path = os.path.join(DATA_PATH, file)

    try:
        os.remove(path)
    except:
        logging.warning(f"Failed to delete file '{path}'!")

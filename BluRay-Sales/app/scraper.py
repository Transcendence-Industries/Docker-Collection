import os
import json
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

import scraper_bluray_disc, scraper_amazon, scraper_jpc, scraper_media_dealer

DATA_PATH = str(os.environ["DATA_PATH"])
PLAYWRIGHT_DRIVER = str(os.environ["PLAYWRIGHT_DRIVER"])
PLAYWRIGHT_RETRIES = int(os.environ["PLAYWRIGHT_RETRIES"])
PLAYWRIGHT_TIMEOUT = int(os.environ["PLAYWRIGHT_TIMEOUT"])

BLURAY_DISC_FILE = "BluRay-Disc.json"
AMAZON_FILE = "Amazon.json"
JPC_FILE = "JPC.json"
MEDIA_DEALER_FILE = "Media-Dealer.json"


def init_scraper(instance):
    logging.info("Connecting scraper...")
    ua = UserAgent()
    user_agent = ua.firefox  # Universal: 'ua.random'

    try:
        browser = instance.chromium.connect_over_cdp(PLAYWRIGHT_DRIVER)
        context = browser.new_context(user_agent=user_agent)
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


def scrape_bluray_disc(search, only_4K=False, only_3D=False):
    request = f"{search}%{only_4K}%{only_3D}"
    result = load_from_json(BLURAY_DISC_FILE)
    result = check_request_json(result, request)

    if not result:
        with sync_playwright() as playwright:
            browser, context = init_scraper(playwright)

            if browser and context:
                curr_try = 1
                result = None

                while not result and curr_try <= PLAYWRIGHT_RETRIES:
                    try:
                        result, _ = scraper_bluray_disc.get_products(context, search, only_4K=only_4K, only_3D=only_3D)
                        save_to_json(BLURAY_DISC_FILE, request, result)
                    except Exception as e:
                        logging.error(e)
                        logging.warning(f"Failed to scrape BluRay-Disc for '{search}' ({curr_try}/{PLAYWRIGHT_RETRIES} tries)!")
                        result = None
                    curr_try += 1

                shutdown_scraper(browser, context)
            else:
                result = None
    else:
        logging.info(f"Loaded cached result for '{request}'.")

    # [ {"name": NAME, "link": LINK, "cover": COVER}, ... ]
    return result


def scrape_amazon(url):
    result = load_from_json(AMAZON_FILE)
    result = check_request_json(result, url)

    if not result:
        with sync_playwright() as playwright:
            browser, context = init_scraper(playwright)

            if browser and context:
                curr_try = 1
                result = None

                while not result and curr_try <= PLAYWRIGHT_RETRIES:
                    try:
                        result = scraper_amazon.get_products(context, url)
                        save_to_json(AMAZON_FILE, url, result)
                    except Exception as e:
                        logging.error(e)
                        logging.warning(f"Failed to scrape Amazon for '{url}' ({curr_try}/{PLAYWRIGHT_RETRIES} tries)!")
                        result = None
                    curr_try += 1

                shutdown_scraper(browser, context)
            else:
                result = None
    else:
        logging.info(f"Loaded cached result for '{url}'.")

    # {NAME: PRICE, ...}
    return result


def scrape_jpc(url):
    result = load_from_json(JPC_FILE)
    result = check_request_json(result, url)

    if not result:
        with sync_playwright() as playwright:
            browser, context = init_scraper(playwright)

            if browser and context:
                curr_try = 1
                result = None

                while not result and curr_try <= PLAYWRIGHT_RETRIES:
                    try:
                        result, _ = scraper_jpc.get_products(context, url)
                        save_to_json(JPC_FILE, url, result)
                    except Exception as e:
                        logging.error(e)
                        logging.warning(f"Failed to scrape JPC for '{url}' ({curr_try}/{PLAYWRIGHT_RETRIES} tries)!")
                        result = None
                    curr_try += 1

                shutdown_scraper(browser, context)
            else:
                result = None
    else:
        logging.info(f"Loaded cached result for '{url}'.")

    # {NAME: PRICE, ...}
    return result


def scrape_media_dealer(url):
    result = load_from_json(MEDIA_DEALER_FILE)
    result = check_request_json(result, url)

    if not result:
        with sync_playwright() as playwright:
            browser, context = init_scraper(playwright)

            if browser and context:
                curr_try = 1
                result = None

                while not result and curr_try <= PLAYWRIGHT_RETRIES:
                    try:
                        result = scraper_media_dealer.get_products(context, url)
                        save_to_json(MEDIA_DEALER_FILE, url, result)
                    except Exception as e:
                        logging.error(e)
                        logging.warning(f"Failed to scrape Media-Dealer for '{url}' ({curr_try}/{PLAYWRIGHT_RETRIES} tries)!")
                        result = None
                    curr_try += 1

                shutdown_scraper(browser, context)
            else:
                result = None
    else:
        logging.info(f"Loaded cached result for '{url}'.")

    # {NAME: PRICE, ...}
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

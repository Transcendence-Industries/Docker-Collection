import os
import json
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

import scraper_youtube

DATA_PATH = str(os.environ["DATA_PATH"])
PLAYWRIGHT_DRIVER = str(os.environ["PLAYWRIGHT_DRIVER"])
PLAYWRIGHT_RETRIES = int(os.environ["PLAYWRIGHT_RETRIES"])
PLAYWRIGHT_TIMEOUT = int(os.environ["PLAYWRIGHT_TIMEOUT"])

YOUTUBE_CHANNEL_FILE = "YouTube-Channel.json"
YOUTUBE_PLAYLIST_FILE = "YouTube-Playlist.json"
YOUTUBE_HIERARCHY_FILE = "YouTube-Hierarchy.json"


def init_scraper(instance):
    logging.info("Connecting scraper...")
    ua = UserAgent()
    user_agent = ua.random  # Universal: 'ua.random'

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


def scrape_channel(url):
    result = load_from_json(YOUTUBE_CHANNEL_FILE)
    result = check_request_json(result, url)

    if not result:
        with sync_playwright() as playwright:
            browser, context = init_scraper(playwright)

            if browser and context:
                curr_try = 1
                result = None

                while not result and curr_try <= PLAYWRIGHT_RETRIES:
                    try:
                        result = scraper_youtube.get_albums(context, url)
                        save_to_json(YOUTUBE_CHANNEL_FILE, url, result)
                    except Exception as e:
                        logging.error(e)
                        logging.warning(f"Failed to scrape YouTube for '{url}' ({curr_try}/{PLAYWRIGHT_RETRIES} tries)!")
                        result = None
                    curr_try += 1

                shutdown_scraper(browser, context)
            else:
                result = None
    else:
        logging.info(f"Loaded cached result for '{url}'.")

    # [ {"name": NAME, "link": LINK, "cover": COVER}, ... ]
    return result


def scrape_playlist(url):
    result = load_from_json(YOUTUBE_PLAYLIST_FILE)
    result = check_request_json(result, url)

    if not result:
        with sync_playwright() as playwright:
            browser, context = init_scraper(playwright)

            if browser and context:
                curr_try = 1
                result = None

                while not result and curr_try <= PLAYWRIGHT_RETRIES:
                    try:
                        result = scraper_youtube.get_tracks(context, url)
                        save_to_json(YOUTUBE_PLAYLIST_FILE, url, result)
                    except Exception as e:
                        logging.error(e)
                        logging.warning(f"Failed to scrape YouTube for '{url}' ({curr_try}/{PLAYWRIGHT_RETRIES} tries)!")
                        result = None
                    curr_try += 1

                shutdown_scraper(browser, context)
            else:
                result = None
    else:
        logging.info(f"Loaded cached result for '{url}'.")

    # [ {"name": NAME, "link": LINK, "cover": COVER}, ... ]
    return result


def generate_hierarchy(url):
    complete = True
    result = load_from_json(YOUTUBE_HIERARCHY_FILE)
    result = check_request_json(result, url)

    if not result:
        result = []
        channel_result = scrape_channel(url)

        if channel_result:
            for album in channel_result:
                tracks = []
                album_result = scrape_playlist(album["link"])

                if album_result:
                    for track in album_result:
                        tracks.append({
                            "name": track["name"],
                            "link": track["link"],
                            "cover": track["cover"]
                        })

                    result.append({
                        "name": album["name"],
                        "link": album["link"],
                        "cover": album["cover"],
                        "tracks": tracks
                    })
                else:
                    complete = False
        else:
            complete = False

        if complete:
            save_to_json(YOUTUBE_HIERARCHY_FILE, url, result)
    else:
        logging.info(f"Loaded cached result for '{url}'.")

    # [ {"name": NAME, "link": LINK, "cover": COVER, "tracks": [ {"name": NAME, "link": LINK, "cover": COVER}, ... ]}, ... ]
    return result, complete


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
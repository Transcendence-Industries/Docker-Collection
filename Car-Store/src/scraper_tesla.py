import time
import logging

import scraper
from models import TeslaModelS, TeslaModel3

BASE_URL = "https://www.tesla.com/de_DE"


def scroll_to_bottom(page, step=1000):
    total_height = page.evaluate("document.body.scrollHeight")
    curr_height = 0

    while curr_height < total_height:
        page.evaluate(f"window.scrollBy(0, {step})")
        curr_height += step
        logging.debug("JPC: Scrolling")
        time.sleep(3)
        total_height = page.evaluate("document.body.scrollHeight")


def get_vehicles(context, filter: TeslaModelS | TeslaModel3):
    request = str(filter)
    logging.info(f"Tesla: Loading request \"{request}\"...")
    page = context.new_page()
    page.goto(f"{BASE_URL}/inventory/{filter.to_url()}",
              timeout=scraper.PLAYWRIGHT_TIMEOUT)
    time.sleep(5)

    logging.info("Tesla: Disabling cookies...")
    button = page.query_selector('button[id="tsla-reject-cookie"]')
    button.click()
    time.sleep(2)

    logging.info("Tesla: Scrolling to bottom...")
    scroll_to_bottom(page)

    no_match = page.query_selector("div.alertbox-content")
    if no_match:
        logging.warning("Tesla: No exact matches found!")
        return [{
            "link": "",
            "pictures": [],
            "name": "NO MATCHES",
            "location": "???",
            "price": "? €",
            "details": "???",
        }]

    articles = page.query_selector_all("article.result.card")

    vehicles = []
    for article in articles:
        order_id = str(article.get_attribute("data-id")).split("-")[0]
        pictures = article.query_selector_all("img.result-image")
        name = article.query_selector("div.trim-name").text_content()
        location = article.query_selector(
            "div.inventory-card-chip").text_content()
        price = article.query_selector(
            "span.tds-text--contrast-high span").text_content()
        details = article.query_selector_all("div.tds-text--contrast-low")

        pictures_filtered = []
        for picture in pictures:
            src = picture.get_attribute("src")
            if src.startswith("https://"):
                pictures_filtered.append(str(src))

        vehicles.append({
            "link": f"{BASE_URL}/{filter.model}/order/{order_id}",
            "pictures": pictures_filtered,
            "name": str(name),
            "location": str(location),
            "price": str(price),
            "details": ", ".join(detail.text_content() for detail in details)
        })

    logging.info(f"Tesla: Found {len(vehicles)} vehicles.")
    page.close()
    return vehicles

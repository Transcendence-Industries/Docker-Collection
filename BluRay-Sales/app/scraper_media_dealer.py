import time
import logging

import scraper


def switch_to_next_page(page):
    button = page.query_selector("a.next")
    if button:
        button.click()
        time.sleep(3)
        return True
    else:
        return False


def get_products(context, url):
    logging.info(f"Media-Dealer: Loading url \"{url}\"...")
    page = context.new_page()
    page.goto(url, timeout=scraper.PLAYWRIGHT_TIMEOUT)
    time.sleep(3)

    products = {}
    has_next = True

    while has_next:
        names = page.query_selector_all("a.title span")
        prices = page.query_selector_all("span.z-productprice")

        for name, price in zip(names, prices):
            name = name.text_content()
            price = price.text_content()
            price = price.replace("\n", "").replace("€", "").replace("*", "").strip()
            products[name] = price

        has_next = switch_to_next_page(page)
        logging.debug(f"Media-Dealer: Going to next page... {has_next}")

    logging.info(f"Media-Dealer: Found {len(products)} products.")
    page.close()
    return products

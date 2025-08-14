import time
import logging

import scraper


def scroll_to_bottom(page, step=1000):
    total_height = page.evaluate("document.body.scrollHeight")
    curr_height = 0

    while curr_height < total_height:
        page.evaluate(f"window.scrollBy(0, {step})")
        curr_height += step
        logging.debug("JPC: Scrolling")
        time.sleep(1)

        button = page.query_selector("button.infinite-load-more--btn")
        if button:
            button.click()
            logging.debug("JPC: Load-More-Button")
            time.sleep(2)
            page.evaluate(f"window.scrollBy(0, {step})")
            curr_height += step
            time.sleep(1)

        total_height = page.evaluate("document.body.scrollHeight")


def get_products(context, url):
    logging.info(f"JPC: Loading url \"{url}\"...")
    page = context.new_page()
    page.goto(url, timeout=scraper.PLAYWRIGHT_TIMEOUT)
    time.sleep(3)

    total_products = page.query_selector("span.pagination small").text_content()
    total_products = int(total_products.split(' ')[0])

    logging.info("JPC: Scrolling to bottom...")
    scroll_to_bottom(page)

    names = page.query_selector_all("div.title")
    prices = page.query_selector_all("div.price strong")
    products = {}

    for name, price in zip(names, prices):
        name = name.text_content()
        price = price.text_content()
        price = price.split(" ")[1].replace("*", "")
        products[name] = price

    logging.info(f"JPC: Found {len(products)}/{total_products} products.")
    page.close()
    got_all = len(products) == total_products
    return products, got_all

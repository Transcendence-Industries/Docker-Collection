import time
import logging

import scraper


def scroll_to_bottom(page, step=1000):
    total_height = page.evaluate("document.body.scrollHeight")
    curr_height = 0

    while curr_height < total_height:
        page.evaluate(f"window.scrollBy(0, {step})")
        curr_height += step
        logging.debug("Amazon: Scrolling")
        time.sleep(1)

        buttonContainer = page.query_selector('div[id="showMoreBtnContainer"]')
        if buttonContainer.is_visible():
            button = page.query_selector("span.showMoreBtn")
            if button:
                button.click()
                logging.debug("Amazon: Load-More-Button")
                time.sleep(2)
                page.evaluate(f"window.scrollBy(0, {step})")
                curr_height += step
                time.sleep(1)

        total_height = page.evaluate("document.body.scrollHeight")


def get_products(context, url):
    logging.info(f"Amazon: Loading url \"{url}\"...")
    page = context.new_page()
    page.goto(url, timeout=scraper.PLAYWRIGHT_TIMEOUT)
    time.sleep(3)

    logging.info("Amazon: Scrolling to bottom...")
    scroll_to_bottom(page)

    names = page.query_selector_all("div.productTitle a")
    prices = page.query_selector_all('span[name="symbolLast"]')

    print(len(names), len(prices))
    products = {}

    for name, price in zip(names, prices):
        name = name.text_content()
        price_whole = price.query_selector("span.a-price-whole").text_content()
        price_fraction = price.query_selector("span.a-price-fraction").text_content()
        price = f"{price_whole},{price_fraction}"
        products[name] = price

    logging.info(f"Amazon: Found {len(products)} products.")
    page.close()
    return products

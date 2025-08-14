import time
import logging

import scraper

SEARCH_URL = "https://bluray-disc.de/suche/"
PREFIX_URL = "https://bluray-disc.de"


def switch_to_next_page(page):
    pager = page.query_selector("div.result-pager")
    sites = pager.query_selector_all("div.colPager")
    index = None

    for index, site in enumerate(sites):
        if "active" in site.get_attribute("class"):
            index += 1
            break

    if index and index < len(sites):
        sites[index].click()
        time.sleep(1)
        return True
    else:
        return False


def get_products(context, search, only_4K, only_3D):
    request = f"{search}%{only_4K}%{only_3D}"
    logging.info(f"BluRay-Disc: Loading request \"{request}\"...")
    page = context.new_page()
    page.goto(SEARCH_URL, timeout=scraper.PLAYWRIGHT_TIMEOUT)
    time.sleep(2)

    logging.info("BluRay-Disc: Disabling cookies...")
    button = page.query_selector("a.cmptxt_btn_no")
    button.click()
    time.sleep(2)

    logging.info("BluRay-Disc: Executing search...")
    option = page.query_selector('label[for="section_movie"]')
    option.click()

    if only_4K:
        option = page.query_selector('label[for="filter_4kuhd"]')
        option.click()
    if only_3D:
        option = page.query_selector('label[for="filter_3d"]')
        option.click()

    field = page.query_selector('input[id="multi_search"]')
    field.fill(search)
    field.press("Enter")
    time.sleep(3)

    button = page.query_selector("div.result-header.toggle")
    button.click()

    total_products = button.query_selector("b span").text_content()
    total_products = int(total_products.replace("(", "").replace(")", ""))

    products = []
    has_next = True

    while has_next:
        results = page.query_selector_all("div.result-item")
        names = [result.query_selector("div.item-info a b").text_content() for result in results]
        links = [result.query_selector("a").get_attribute("href") for result in results]
        covers = [result.query_selector("a img").get_attribute("src") for result in results]

        for name, link, cover in zip(names, links, covers):
            if not link.startswith(PREFIX_URL):
                link = PREFIX_URL + link
            if not cover.startswith(PREFIX_URL):
                cover = PREFIX_URL + cover

            products.append({
                "name": str(name),
                "link": str(link),
                "cover": str(cover)
            })

        has_next = switch_to_next_page(page)
        logging.debug(f"BlueRay-Disc: Going to next page... {has_next}")

    logging.info(f"BlueRay-Disc: Found {len(products)}/{total_products} products.")
    page.close()
    got_all = len(products) == total_products
    return products, got_all

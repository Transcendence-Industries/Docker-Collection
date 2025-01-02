import time
import logging

import scraper

PREFIX_URL = "https://www.youtube.com"


def disable_cookies(page):
    logging.info("YouTube: Disabling cookies...")
    button = page.query_selector('//span[text()="Reject all"]')
    button.click()
    time.sleep(3)


def get_albums(context, url):
    logging.info(f"YouTube: Loading url \"{url}\"...")
    page = context.new_page()
    page.goto(url, timeout=scraper.PLAYWRIGHT_TIMEOUT)
    time.sleep(3)

    disable_cookies(page)

    logging.info("YouTube: Showing all albums...")
    button = page.query_selector('button[aria-label="View all"]')
    button.click()
    time.sleep(1)

    # TODO: Maybe scroll down to load all cover images

    albums = []
    blocks = page.query_selector_all("ytd-grid-playlist-renderer")
    for block in blocks:
        name = block.query_selector('a[id="video-title"]').text_content()
        link = block.query_selector('//a[text()="View full playlist"]').get_attribute("href")
        cover = block.query_selector("img").get_attribute("src")

        if not link.startswith(PREFIX_URL):
            link = PREFIX_URL + link

        albums.append({
            "name": str(name),
            "link": str(link),
            "cover": str(cover)
        })

    logging.info(f"YouTube: Found {len(albums)} albums.")
    page.close()
    return albums


def get_tracks(context, url):
    logging.info(f"YouTube: Loading url \"{url}\"...")
    page = context.new_page()
    page.goto(url, timeout=scraper.PLAYWRIGHT_TIMEOUT)
    time.sleep(3)

    disable_cookies(page)

    # TODO: Maybe scroll down to load all cover images

    tracks = []
    blocks = page.query_selector_all("ytd-playlist-video-renderer")
    for block in blocks:
        name = block.query_selector('a[id="video-title"]').text_content()
        link = block.query_selector('a[id="video-title"]').get_attribute("href")
        cover = block.query_selector("img").get_attribute("src")

        if not link.startswith(PREFIX_URL):
            link = PREFIX_URL + link

        name = str(name).replace("\n", "").strip()

        tracks.append({
            "name": str(name),
            "link": str(link),
            "cover": str(cover)
        })

    logging.info(f"YouTube: Found {len(tracks)} tracks.")
    page.close()
    return tracks

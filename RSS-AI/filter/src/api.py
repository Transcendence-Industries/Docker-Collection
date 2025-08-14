import os
import logging
import hashlib
import requests
from datetime import datetime

FRESHRSS_URL = str(os.environ["FRESHRSS_URL"])
FRESHRSS_USER = str(os.environ["FRESHRSS_USER"])
FRESHRSS_PASSWORD = str(os.environ["FRESHRSS_PASSWORD"])


token = hashlib.md5(
    f"{FRESHRSS_USER}:{FRESHRSS_PASSWORD}".encode()).hexdigest()


def fetch_groups():
    # ['api_version', 'auth', 'last_refreshed_on_time', 'groups', 'feeds_groups']
    # ['id', 'title']

    response = requests.post(
        url=f"{FRESHRSS_URL}/api/fever.php?api&groups", data={"api_key": token})
    response_json = response.json()
    result = []

    # Add 'feed_ids' to groups
    for mapping in response_json["feeds_groups"]:
        group_id = mapping["group_id"]
        feed_ids = mapping["feed_ids"]

        for group in response_json["groups"]:
            if group["id"] == group_id:
                result.append({
                    **group,
                    "feed_ids": [int(num) for num in feed_ids.split(",")]
                })

    # ['id', 'title', 'feed_ids']
    logging.debug(f"Fetched {len(result)} groups.")
    return result


def fetch_feeds():
    # ['api_version', 'auth', 'last_refreshed_on_time', 'feeds', 'feeds_groups']
    # ['id', 'favicon_id', 'title', 'url', 'site_url', 'is_spark', 'last_updated_on_time']

    response = requests.post(
        url=f"{FRESHRSS_URL}/api/fever.php?api&feeds", data={"api_key": token})
    result = response.json()["feeds"]

    logging.debug(f"Fetched {len(result)} feeds.")
    return result


def fetch_articles():
    # ['api_version', 'auth', 'last_refreshed_on_time', 'total_items', 'items']
    # ['id', 'feed_id', 'title', 'author', 'html', 'url', 'is_saved', 'is_read', 'created_on_time']

    result = []

    response = requests.post(
        url=f"{FRESHRSS_URL}/api/fever.php?api&items", data={"api_key": token})
    batch = response.json()["items"]
    last_id = batch[-1]["id"]
    result.extend(batch)
    logging.debug(f"Fetched a batch of {len(batch)} articles.")

    total = response.json()["total_items"]

    # Fetch all articles
    while len(result) < total:
        response = requests.post(
            url=f"{FRESHRSS_URL}/api/fever.php?api&items&since_id={last_id}", data={"api_key": token})
        batch = response.json()["items"]
        last_id = batch[-1]["id"]
        result.extend(batch)
        logging.debug(f"Fetched a batch of {len(batch)} articles.")

    # Sort articles with descending datetime
    result = sorted(result, key=lambda article: datetime.fromtimestamp(
        article["created_on_time"]), reverse=True)

    logging.debug(f"Fetched a total of {len(result)} articles.")
    return result


def filter_articles(articles, feed_id, dt):
    result = []

    for article in articles:
        if article["feed_id"] != feed_id:
            continue

        article_dt = datetime.fromtimestamp(article["created_on_time"])
        if article_dt.date() != dt.date():
            continue

        result.append(article)

    return result

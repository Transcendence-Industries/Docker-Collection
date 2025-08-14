import os
import json
import logging
from datetime import datetime
from email.utils import format_datetime
from flask import Flask, Response
from feedgen.feed import FeedGenerator

DATA_PATH = str(os.environ["DATA_PATH"])
FEED_NAME = str(os.environ["FEED_NAME"])
FEED_DESCRIPTION = str(os.environ["FEED_DESCRIPTION"])
FEED_LINK = str(os.environ["FEED_LINK"])

FEED_FILE = "feed.json"
ARTICLES_FILE = "articles.json"

app = Flask(__name__)


def load_stats():
    try:
        with open(os.path.join(DATA_PATH, FEED_DESCRIPTION), mode="r", encoding="utf-8") as file:
            stats = json.load(file)

        logging.debug("Loaded stats.")
        return stats
    except:
        logging.warning("Failed to load stats!")
        return None


def load_articles():
    try:
        with open(os.path.join(DATA_PATH, ARTICLES_FILE), mode="r", encoding="utf-8") as file:
            articles = json.load(file)

        logging.debug(f"Loaded {len(articles)} articles.")
        return articles
    except:
        logging.warning("Failed to load articles!")
        return []


@app.route("/")
def default():
    return Response("Hello, World!")


@app.route("/rss")
def rss():
    logging.info("Providing RSS feed...")
    stats = load_stats()
    articles = load_articles()

    fg = FeedGenerator()
    fg.title(FEED_NAME)
    fg.description(FEED_DESCRIPTION)
    fg.link(href=FEED_LINK, rel="alternate")

    if stats:
        fg.lastBuildDate(format_datetime(datetime.fromtimestamp(stats["last_update"])))
    else:
        fg.lastBuildDate(format_datetime(datetime.now()))

    for article in articles:
        logging.debug(f"Preparing article '{article['title']}'...")

        fe = fg.add_entry()
        fe.title(article["title"])
        fe.description(article["description"])
        fe.content(article["content"])
        fe.pubDate(format_datetime(datetime.fromtimestamp(article["datetime"])))
        fe.link(href=article["link"])

    rss_str = fg.rss_str(pretty=True)
    logging.info(f"Prepared RSS feed with {len(articles)} articles.")
    return Response(rss_str, mimetype="application/rss+xml")

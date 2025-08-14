import os
import json
import logging
from datetime import datetime, timedelta

from ai import summarize_article, prioritize_articles
from api import fetch_groups, fetch_feeds, fetch_articles, filter_articles

DATA_PATH = str(os.environ["DATA_PATH"])
EXCLUDED_GROUP_IDS = str(os.environ["EXCLUDED_GROUP_IDS"]).split(",")
EXCLUDED_FEED_IDS = str(os.environ["EXCLUDED_FEED_IDS"]).split(",")
MAX_ARTICLES_PER_FEED = int(os.environ["MAX_ARTICLES_PER_FEED"])
MAX_PREVIOUS_DAYS = int(os.environ["MAX_PREVIOUS_DAYS"])

FEED_FILE = "feed.json"
ARTICLES_FILE = "articles.json"


def load_articles():
    try:
        with open(os.path.join(DATA_PATH, ARTICLES_FILE), mode="r", encoding="utf-8") as file:
            output = json.load(file)

        logging.debug(f"Loaded {len(output)} articles.")
    except:
        output = []
        logging.warning("Failed to load articles!")

    return output


def save_articles(articles):
    output = []

    for article in articles:
        data = {
            "title": article["title"],
            "description": "",
            "content": article["content"],
            "datetime": article["datetime"],
            "link": "",
        }

        if "description" in article.keys():
            data["description"] = article["description"]

        if "link" in article.keys():
            data["link"] = article["link"]
        elif "url" in article.keys():
            data["url"] = article["url"]

        output.append(data)

    try:
        with open(os.path.join(DATA_PATH, ARTICLES_FILE), mode="w", encoding="utf-8") as file:
            json.dump(output, file, indent=4)

        logging.debug(f"Saved {len(output)} articles.")
    except:
        logging.warning("Failed to save articles!")


def save_stats():
    stats = {
        "last_update": datetime.now().timestamp()
    }

    try:
        with open(os.path.join(DATA_PATH, FEED_FILE), mode="w", encoding="utf-8") as file:
            json.dump(stats, file, indent=4)

        logging.debug("Saved stats.")
    except:
        logging.warning("Failed to save stats!")


def main_run():
    logging.info("Starting AI run...")
    existing_articles = load_articles()
    output_articles = []

    groups = fetch_groups()
    feeds = fetch_feeds()
    articles = fetch_articles()
    today = datetime.today()

    groups = [group for group in groups if str(
        group["id"]) not in EXCLUDED_GROUP_IDS]
    feeds = [feed for feed in feeds if str(
        feed["id"]) not in EXCLUDED_FEED_IDS]
    articles = [article for article in articles if str(
        article["feed_id"]) not in EXCLUDED_FEED_IDS]
    logging.info(f"Fetched {len(groups)} groups.")
    logging.info(f"Fetched {len(feeds)} feeds.")
    logging.info(f"Fetched {len(articles)} articles.")

    for days in range(MAX_PREVIOUS_DAYS + 1):
        dt = today - timedelta(days=days)
        logging.debug(f"Processing day '{dt.date()}'...")

        for group in groups:
            existing = next((a for a in existing_articles if a["group_id"] == group["id"]
                            and datetime.fromtimestamp(a["datetime"]).date() == dt.date()), None)

            if existing:
                logging.debug(f"> Recycling group '{group['title']}'...")
                output_articles.append(existing)
            else:
                logging.debug(f"> Processing group '{group['title']}'...")
                content = ""

                for feed_id in group["feed_ids"]:
                    feed = next(
                        feed for feed in feeds if feed["id"] == feed_id)
                    logging.debug(f">> Processing feed '{feed['title']}'...")

                    content += "<hr>"
                    content += f"<h2>{feed['title']}</h2>"

                    filtered_articles = filter_articles(
                        articles=articles, feed_id=feed_id, dt=dt)

                    if len(filtered_articles) > MAX_ARTICLES_PER_FEED:
                        filtered_articles = filtered_articles[:MAX_ARTICLES_PER_FEED]

                    for article in filtered_articles:
                        logging.debug(
                            f">>> Processing article '{article['title']}'...")
                        article_sum = summarize_article(article)
                        article_sum = article_sum.replace("\n", "")

                        content += f"<p>{article_sum}</p>"

                output_articles.append({
                    "title": f"Zusammenfassung von Kategorie '{group['title']}'",
                    "content": content,
                    "datetime": dt.timestamp(),
                    "group_id": group["id"],
                })

    if output_articles:
        logging.info(f"Prepared {len(output_articles)} articles.")
        save_articles(output_articles)
        save_stats()
    else:
        logging.info("Prepared no articles.")

    logging.info("Done!")

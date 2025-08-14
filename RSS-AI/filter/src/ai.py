import os
import logging
from ollama import Client
from bs4 import BeautifulSoup

OLLAMA_URL = str(os.environ["OLLAMA_URL"])
OLLAMA_MODEL = str(os.environ["OLLAMA_MODEL"])

client = Client(host=OLLAMA_URL)


def extract_text_from_html(html_code):
    soup = BeautifulSoup(html_code, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")  # optional: use " " for inline flow
    lines = [line.strip() for line in text.splitlines()]
    cleaned_text = "\n".join(line for line in lines if line)

    return cleaned_text


def summarize_article(article):
    title = str(article["title"])
    content = extract_text_from_html(article["html"])
    logging.debug(f"Summarizing article '{title}'...")

    prompt = f"""
    Fasse den folgenden News-Artikel in einem Absatz zusammen.
    Verwende die gleiche Sprache wie der original Text.
    Gib nur die Zusammenfassung zurück.

    {content}
    """

    response = client.generate(model=OLLAMA_MODEL, prompt=prompt)
    return response.response


def prioritize_articles(articles):
    titles = [article["title"] for article in articles]
    logging.debug(f"Prioritizing articles '{titles}'...")

    prompt = f"""
    Du bist ein Assistent zur Priorisierung von News-Artikeln.
    Bewerte nach den Kriterien: globale Auswirkungen, öffentliche Relevanz, Dringlichkeit und Glaubwürdigkeit der Quelle
    Die folgende Liste enthält die Artikel, welche du absteigend nach ihrer Relevanz sortieren sollst.
    Gib nur eine Auflistung der Artikelnummern zurück.
    """
    prompt += "\n"

    for i, article in enumerate(articles, start=1):
        title = str(article["title"])
        prompt += f"\n{i}: {title}"

    response = client.generate(model=OLLAMA_MODEL, prompt=prompt)
    ids = str(response.response).replace(" ", "").replace("\n", "").split(",")
    result = []

    for id in set(ids):
        try:
            result.append(articles[int(id) - 1])
        except:
            logging.warning("Invalid ID while filtering articles!")

    return result

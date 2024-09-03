import os
import re
import pandas as pd
import streamlit as st
from datetime import datetime

import scraper

DATABASE_FILE_PREFIX = "Upload"
NECCESSARY_COLUMNS = ["Titel", "Kommentar", "Angesehen", "Bewertung", "Typ", "Medium"]
CACHE_FILES = (scraper.BLURAY_DISC_FILE, scraper.AMAZON_FILE, scraper.JPC_FILE, scraper.MEDIA_DEALER_FILE)


def compare_titles(result, search):
    result = re.sub(r'\(.*?\)', '', result).replace("Blu-Ray", "").strip().lower()
    search = search.strip().lower()
    return search == result


def filter_results(results, names):  # TODO: No originals, ...
    filtered = {}

    for name in names:
        for result in results:
            if compare_titles(result["name"], name):
                filtered[name] = result
                break

    return filtered


def load_csv(file):
    df = None
    success = True

    try:
        df = pd.read_csv(file)

        for column in NECCESSARY_COLUMNS:
            if column not in df.columns:
                success = False
                break
    except:
        success = False

    return df, success


def save_csv(file, df):
    try:
        df.to_csv(file, index=False)
        return True
    except:
        return False


def clone_csv(file):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{DATABASE_FILE_PREFIX}_{timestamp}.csv"
    path = os.path.join(scraper.DATA_PATH, file_name)

    try:
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        return True
    except:
        return False


def check_availability(progress, file, only_4K=False, only_3D=False):
    df, success = load_csv(file)
    column = None

    if df is not None and success:
        if only_4K:
            column = "4K_available"
            if "4K_available" not in df.columns:
                df["4K_available"] = ""
        elif only_3D:
            column = "3D_available"
            if "3D_available" not in df.columns:
                df["3D_available"] = ""
        else:
            column = "available"
            if "available" not in df.columns:
                df["available"] = ""

        if column:
            for index, row in df.iterrows():
                if row[column] != "Yes" and row[column] != "No" and "Original" in row["Typ"]:
                    found = False
                    search_name = row["Titel"]
                    results = scraper.scrape_bluray_disc(search_name, only_4K=only_4K, only_3D=only_3D)

                    if results:
                        for result in results:
                            result_name = result["name"]

                            if only_4K:
                                result_name = result_name.replace("4K", "").strip()
                            if only_3D:
                                result_name = result_name.replace("3D", "").strip()

                            if compare_titles(result_name, search_name):
                                df.at[index, column] = "Yes"
                                found = "No"
                                break

                        if not found:
                            df.at[index, column] = True
                    else:
                        df.at[index, column] = ""

                progress.progress(int((index + 1) / len(df) * 100))

        return save_csv(file, df)
    else:
        return False


def main():
    st.set_page_config(page_title="BluRay Sales", layout="centered")
    st.title("BluRay Sales - Interface")

    # ------------------------------

    st.header("Movie search")
    only_4K = st.checkbox("4K only")
    only_3D = st.checkbox("3D only")
    search = st.text_input("Enter a movie")

    if search:
        search_result = scraper.scrape_bluray_disc(search, only_4K, only_3D)
        if search_result:
            # st.write(search_result)
            for elem in search_result:
                st.image(elem["cover"], caption=elem["name"])
                st.markdown(f"[More info]({elem['link']})")
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.error("Something went wrong!")

    # ------------------------------

    st.header("Movie database")
    db_file = st.file_uploader("Upload a CSV file", type="csv")
    db_selection = st.selectbox("Choose a CSV file", [file for file in os.listdir(scraper.DATA_PATH) if file.startswith(DATABASE_FILE_PREFIX)])
    df = None
    success = False

    if db_file:
        if clone_csv(db_file):
            st.success("Success! Please reload the site.")
        else:
            st.error("Failed to save the uploaded CSV file!")

    if db_selection:
        db_path = os.path.join(scraper.DATA_PATH, db_selection)
        df, success = load_csv(db_path)
        if not success:
            st.error("CSV file has the wrong format!")
        elif df is None:
            st.error("Failed to load selected CSV file!")
        else:
            st.write(df)

    # ------------------------------

    progress = st.progress(0)

    if st.button("Check availability"):
        if df is not None and success:
            progress.empty()

            if check_availability(progress, db_path):
                st.success("Success! Please reload the site.")
            else:
                st.error("Something went wrong!")
        else:
            st.error("No database loaded!")

    if st.button("Check 4K availability"):
        if df is not None and success:
            progress.empty()

            if check_availability(progress, db_path, only_4K=True):
                st.success("Success! Please reload the site.")
            else:
                st.error("Something went wrong!")
        else:
            st.error("No database loaded!")

    if st.button("Check 3D availability"):
        if df is not None and success:
            progress.empty()

            if check_availability(progress, db_path, only_3D=True):
                st.success("Success! Please reload the site.")
            else:
                st.error("Something went wrong!")
        else:
            st.error("No database loaded!")

    # ------------------------------

    sale_url = st.text_input("Enter a sale URL")
    shop_result = None

    if db_file and sale_url:
        if sale_url.startswith("https://www.amazon.de/"):
            shop_result = scraper.scrape_amazon(sale_url)
        elif sale_url.startswith("https://www.jpc.de/"):
            shop_result = scraper.scrape_jpc(sale_url)
        elif sale_url.startswith("https://www.media-dealer.de/"):
            shop_result = scraper.scrape_media_dealer(sale_url)
        else:
            st.error("Unknown sale URL!")

        if shop_result:
            st.write(filter_results(shop_result))
        else:
            st.error("Something went wrong!")

    # ------------------------------

    st.header("Delete cache")
    delete_selection = st.selectbox("Choose a file", CACHE_FILES)

    if st.button("Delete"):
        if delete_selection:
            scraper.delete_json(delete_selection)

import streamlit as st

import scraper

CACHE_FILES = (scraper.YOUTUBE_CHANNEL_FILE, scraper.YOUTUBE_PLAYLIST_FILE, scraper.YOUTUBE_HIERARCHY_FILE)


def main():
    st.set_page_config(page_title="YouTube Music", layout="centered")
    st.title("YouTube Music - Interface")

    # ------------------------------

    st.header("Channel search")
    channel = st.text_input("Enter a channel URL")

    if channel:
        channel_result = scraper.scrape_channel(channel)
        if channel_result:
            # st.write(channel_result)
            for elem in channel_result:
                st.image(elem["cover"], caption=elem["name"])
                st.markdown(f"[More info]({elem['link']})")
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.error("Something went wrong!")

    # ------------------------------

    st.header("Album/Playlist search")
    playlist = st.text_input("Enter an album/playlist URL")

    if playlist:
        playlist_result = scraper.scrape_playlist(playlist)
        if playlist_result:
            # st.write(playlist_result)
            for elem in playlist_result:
                st.image(elem["cover"], caption=elem["name"])
                st.markdown(f"[More info]({elem['link']})")
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.error("Something went wrong!")

    # ------------------------------

    st.header("Create hierarchy")
    channel_2 = st.text_input("Enter a channel URL ")

    if channel_2:
        hierarchy, complete = scraper.generate_hierarchy(channel_2)
        if complete:
            st.write(hierarchy)
        else:
            st.write(hierarchy)
            st.warning("This result is missing some elements!")

    # ------------------------------

    st.header("Delete cache")
    delete_selection = st.selectbox("Choose a file", CACHE_FILES)

    if st.button("Delete"):
        if delete_selection:
            scraper.delete_json(delete_selection)


main()

import streamlit as st

import scraper
from models import TeslaModelS, TeslaModel3

CACHE_FILES = (scraper.TESLA_FILE,)


def main():
    st.set_page_config(page_title="Car Store", layout="centered")
    st.title("Car Store - Interface")

    # ------------------------------

    st.header("Tesla Inventory")

    zipcode = st.text_input("Enter a zipcode", value="0")
    model = st.segmented_control(
        "Model", selection_mode="single", options=["Model S", "Model 3"], default="Model S")

    model_type = TeslaModelS if model == "Model S" else TeslaModel3

    type = st.segmented_control(
        "Type", selection_mode="single", options=model_type.options("type"))
    engines = st.segmented_control(
        "Engines", selection_mode="multi", options=model_type.options("engines"))
    exterior_colors = st.segmented_control(
        "Exterior Colors", selection_mode="multi", options=model_type.options("exterior_colors"))
    interior_colors = st.segmented_control(
        "Interior Colors", selection_mode="multi", options=model_type.options("interior_colors"))
    years = st.segmented_control(
        "Years", selection_mode="multi", options=model_type.options("years"))

    if st.button("Search"):
        if all(var for var in (zipcode, model, type)):
            filter = model_type(zipcode=zipcode,
                                type=type,
                                model=model.lower().replace("model ", "m"),
                                engines=engines,
                                exterior_colors=exterior_colors,
                                interior_colors=interior_colors,
                                years=years)
            result = scraper.scrape_tesla(filter)

            if result is not None:
                if len(result) > 0:
                    # st.write(result)
                    for elem in result:
                        st.markdown(f"# {elem['name']} ({elem['location']})")
                        for img in elem["pictures"]:
                            st.image(img)
                        st.markdown(f"### {elem['price']}")
                        st.markdown(f"> {elem['details']}")
                        st.markdown(f"[More info]({elem['link']})")
                        st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.warning("No matches found!")
            else:
                st.error("Something went wrong!")
        else:
            st.error("Invalid filtering options!")

    # ------------------------------

    st.header("Delete cache")
    delete_selection = st.selectbox("Choose a file", CACHE_FILES)

    if st.button("Delete"):
        if delete_selection:
            scraper.delete_json(delete_selection)


main()

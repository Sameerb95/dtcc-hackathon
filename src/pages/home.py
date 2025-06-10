# src/pages/home.py
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import os
from pathlib import Path
from typing import Optional


try:
    from .new_regulation import init_db, RESOURCE_PATH 
except ImportError:
    try:
        from pages.new_regulation import init_db, RESOURCE_PATH
    except ImportError:
        st.error("Could not import DB functions from new_regulation.py.")
        init_db = None
        RESOURCE_PATH = "resources"


def main():
    st.set_page_config(layout="wide")

    if init_db:
        init_db()

    # --- Sidebar ---
    st.sidebar.page_link(page="pages/home.py", label="Home")
    st.sidebar.page_link(page="pages/new_regulation.py", label="Add New Regulation (V1)")
    st.sidebar.page_link(page="pages/changes_review.py", label="review changes")
    st.sidebar.page_link(page="pages/view_graphs.py", label="graph")

    

    add_vertical_space(1)
    st.title("Document Processing and Analysis Hub")
    st.markdown("Welcome! Use the sidebar to navigate to different functionalities.")
    add_vertical_space(2)


    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Compare with New Version (V2)", key="compare_v2_home_nav"):
            st.switch_page("pages/add_new_version.py")

        if st.button("Show Summary", key="show_summary_home_main", disabled=True): # Kept as is
            st.info("Functionality to show summary to be implemented.")

    with col2:
        if st.button("Show Difference Graphs", key="show_graphs_home_main"): # Enabled and action added
            st.switch_page("pages/view_graphs.py")
        if st.button("Show BRD", key="show_brd_home_main", disabled=True): # Kept as is
            st.info("Functionality to show BRD to be implemented.")

    with col3:
        if st.button("Show KOP", key="show_kop_home_main", disabled=True): # Kept as is
            st.info("Functionality to show KOP to be implemented.")

if __name__ == "__main__":
    main()

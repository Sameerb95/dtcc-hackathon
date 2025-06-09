import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space


def main():
    st.set_page_config(layout="wide")

    # Sidebar for navigation
    st.sidebar.page_link(page="pages/home.py", label="Home")
    st.sidebar.page_link(page="pages/new_regulation.py", label="Add New Regulation")

    add_vertical_space(1)

if __name__ == "__main__":
    main()
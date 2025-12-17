import streamlit as st

st.set_page_config(layout="wide")

hide_menu_style = """
        <style>
            [data-testid="stSidebar"]{
            min-width: 0px;
            max-width: 200px;
            }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.title("🏛️ About")

st.markdown(
    """
This Streamlit app explores ancient Roman graffiti from Pompeii and Herculaneum (Latin and Greek inscriptions) using basic cleaning, translation experiments, and NLP topic modeling.

In many ways, these wall inscriptions are the ancient version of “writing on the wall” today: short, informal messages that capture everyday voices and social life. This project was a short class-driven exploration of what we *can* and *can’t* learn from imperfect data and limited modern language models—especially for ancient languages—while still surfacing some interesting patterns and examples.

**Course context**

This project was created for a Tufts University class during Spring 2023: [CLS 191: Natural Language Processing and the Human Record](https://sites.tufts.edu/perseusupdates/2022/10/31/spring-2023-course-on-natural-language-processing-and-the-human-record/).

**Code & details**

You can read the source code in the GitHub repository: [github.com/fisher-c/graffiti](https://github.com/fisher-c/graffiti).
"""
)

import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout='wide')
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

st.header("Data")

st.subheader("Dataset")
st.markdown(
    """
The dataset is downloaded from the Ancient Graffiti Project (AGP) website (http://ancientgraffiti.org/Graffiti/). AGP is a digital resource and search engine for locating and studying graffiti of the early Roman empire from the cities of Pompeii and Herculaneum. It was founded in 2012 by Rebecca Benefiel and Holly Sypniewski, both professors of classics at the University of Mississippi. The AGP website includes a searchable database of over 1,600 graffiti inscriptions from Pompeii and Herculaneum. These inscriptions are accompanied by translations, transcriptions, and photographs. The website also includes a map of the ancient cities, which allows users to see where the graffiti was found.

The dataset used in this study consists of 2124 entries and **22 columns** after flattening the nested JSON data and dropping a few columns related to contributors. The resulting columns of the dataset include `content`, `apparatus`, `sourceFindSpot`, `contentTranslation`, `caption`, `writingStyleInEnglish`, `languageInEnglish`, `cil`, `citation`, `preciseLocation`, `italianPropertyName`, `numberOfGraffiti`, `propertyNumber`, `insula.shortName`, `insula.fullName`, `insula.city.name`, `insula.city.pleiadesId`, `englishPropertyName`, `additionalEntrances`, `propertyName`, `descriptionInEnglish`, and `descriptionInLatin`.

For the purposes of NLP and text analysis, we focused on three columns: `content` (original wall text with annotations), `contentTranslation`, and `languageInEnglish` (either Latin, Greek, or Latin/Greek). Notably, the dataset only has 1030 translated values (48.5%). Missing values are handled during data preprocessing. The dataset is shown in the table below.
"""
)

# read csv
df = pd.read_csv('data/df.csv', encoding='utf-8')

COLOR_SCALE = ["#DDF7EF", "#1B7F6A"]  # light -> dark mint/teal


def bar_counts(series, *, x_label: str, title: str):
    counts = series.value_counts().reset_index()
    counts.columns = [x_label, "Count"]
    fig = px.bar(
        counts,
        x=x_label,
        y="Count",
        color="Count",
        color_continuous_scale=COLOR_SCALE,
        labels={x_label: x_label, "Count": "Graffiti count"},
        opacity=0.9,
    )
    fig.update_layout(title=title, xaxis_title="", yaxis_title="Graffiti count")
    fig.update_layout(height=360)
    fig.update_coloraxes(showscale=False)
    return fig


_pad_left, _center, _pad_right = st.columns([1, 6, 1])
with _center:
    fig = bar_counts(
        df["insula.fullName"],
        x_label="Insula",
        title="Number of graffiti by insula (city block)",
    )
    st.plotly_chart(fig, use_container_width=True)


_pad_left, col1, col2, _pad_right = st.columns([1, 3, 3, 1])
with col1:
    fig = bar_counts(
        df["insula.city.name"],
        x_label="City",
        title="Number of graffiti by city",
    )
    st.plotly_chart(fig, use_container_width=True)


with col2:
    fig = bar_counts(
        df["languageInEnglish"],
        x_label="Language",
        title="Number of graffiti by language",
    )
    st.plotly_chart(fig, use_container_width=True)


content_df = df[['content', 'contentTranslation', 'languageInEnglish']]
# streamlit show dataframe
st.dataframe(content_df)


st.subheader("Data Preprocessing")
st.markdown(
    """
Raw inscriptions from the Ancient Graffiti Project include a lot of scholarly markup (brackets, symbols, editorial notes) based on their [epigraphic conventions](http://ancientgraffiti.org/about/main/epigraphic-conventions/). To make the text usable for translation and NLP, we cleaned and normalized these annotations while trying to preserve what was actually written on the wall.

In short, we:

1. Removed empty or clearly invalid rows.
2. Decoded HTML entities and normalized casing/whitespace.
3. Simplified common annotation patterns (e.g., turning `a(bc)` into `abc`) while preserving missing-text markers like `[---]`.
4. Removed remaining special characters and formatting noise.
5. Ran a small “text infilling” experiment for `[---]` gaps using language models (LatinBERT for Latin and GreekBERT for Greek). This step is inherently imperfect because many inscriptions are extremely short and fragmentary.
"""
)

with st.expander("See detailed cleaning rules"):
    st.markdown(
        """
These rules were implemented primarily with regular expressions (here `abc` stands for any letters):

1. Drop rows with missing values.
2. If a row contains `ABC`, drop the row.
3. Decode HTML entities into their corresponding characters.
4. If the pattern `(:abc)` appears, replace the previous word with `abc`.
5. Remove `?`.
6. Replace `((:abc))` with `abc`.
7. Replace `a(bc)` with `abc`.
8. Replace `[abc]` and `[[abc]]` with `abc`, and normalize `[ab c]` → `ab c` (but keep `[---]` as-is).
9. Convert text to lowercase.
10. Remove `+`.
11. Replace newlines (`\\n`) with `, `.
12. Remove `〈 〉` and `< >` and everything in between.
13. Remove `〚〛` and everything in between.
14. Text infilling for `[---]` (LatinBERT for Latin and GreekBERT for Greek).
15. Remove remaining special characters.
"""
    )

# read data
latin_content = pd.read_csv('data/latin_content.csv', encoding='utf-8')
greek_content = pd.read_csv('data/greek_content.csv', encoding='utf-8')

st.write("A comparison of the raw Latin text and the preprocessed Latin texts is shown below:")

st.dataframe(latin_content)

st.write("Greek content: ")

st.dataframe(greek_content)

st.subheader("Translation")

"""
The graffiti content translation, `contentTranslation` column, has 51% missing value; thus we decided to use use Google translate to translate Greek and Latin texts to English. The data preprocessing steps helped improve the translation results. However, since there are too many missing letters, alphabets, and words, the translation results are not very accurate. Once we got the translations, we replaced the NaN translation values with the google translate result. The translation results are shown below: 
"""
latin_translated = pd.read_csv('data/latin_translated.csv', encoding='utf-8')
greek_cranslated = pd.read_csv('data/greek_translated.csv', encoding='utf-8')

st.write("Latin:")
st.dataframe(
    latin_translated[["content", "preprocessed", "contentTranslation"]])

st.write("Greek: ")
st.dataframe(
    greek_cranslated[["content", "preprocessed", "contentTranslation"]])


"""
Finally, we dropped rows where the translation is describing letters and alphabets (translations that don't contain any actual meanings). For example, in the Greek translation, we dropped rows where the translation contains "alphabet" and "Incomprehensible series of characters". In the Latin translation, we dropped rows where the translation contains "letter", "unkown meaning", "Beginning of a word", etc. The final size of dataframe after dropping those rows is 1569. We used the results for the topic modeling tasks.
"""

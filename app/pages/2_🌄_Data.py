import pandas as pd
import streamlit as st
import plotly.graph_objs as go
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
"""
The dataset is downloaded from the Ancient Graffiti Project (AGP) website (http://ancientgraffiti.org/Graffiti/). AGP is a digital resource and search engine for locating and studying graffiti of the early Roman empire from the cities of Pompeii and Herculaneum. It was founded in 2012 by Rebecca Benefiel and Holly Sypniewski, both professors of classics at the University of Mississippi. The AGP website includes a searchable database of over 1,600 graffiti inscriptions from Pompeii and Herculaneum. These inscriptions are accompanied by translations, transcriptions, and photographs. The website also includes a map of the ancient cities, which allows users to see where the graffiti was found.

The dataset used in this study consists of 2124 entries and 22 columns after flattening the nested JSON data and dropping a few columns related to contributors. The resulting columns of the dataset include 'content', 'apparatus', 'sourceFindSpot', 'contentTranslation', 'caption', 'writingStyleInEnglish', 'languageInEnglish', 'cil', 'citation', 'preciseLocation', 'italianPropertyName', 'numberOfGraffiti', 'propertyNumber', 'insula.shortName', 'insula.fullName', 'insula.city.name', 'insula.city.pleiadesId', 'englishPropertyName', 'additionalEntrances', 'propertyName', 'descriptionInEnglish', and 'descriptionInLatin'. 

For the purposes of natural language processing and text analysis, we focused on three columns: content (original wall text with annotations), contentTranslation, and languageInEnglish (either Latin, Greek, or Latin/Greek). It is note-worthy that the dataset only has 1030 translated content, which is only 48.5% of the values. The missing values will be dealt with during data preprocessing. The dataset is shown in the table below.
"""

# read csv
df = pd.read_csv('data/df.csv', encoding='utf-8')

counts = df['insula.fullName'].value_counts()
fig = px.bar(x=counts.index, y=counts.values, labels={'x': 'Insula', 'y': 'Count'},
             color_discrete_sequence=['#9EE6CF'], opacity=0.9)
fig.update_layout(title='Insula Distribution',
                  xaxis_title='', yaxis_title='Count')
st.plotly_chart(fig)


counts = df['insula.city.name'].value_counts()
fig = px.bar(x=counts.index, y=counts.values, labels={'x': 'City', 'y': 'Count'},
             color_discrete_sequence=['#9EE6CF'], opacity=0.9)
fig.update_layout(title='City Distribution',
                  xaxis_title='', yaxis_title='Count')
st.plotly_chart(fig)


counts = df['languageInEnglish'].value_counts()
fig = px.bar(x=counts.index, y=counts.values, labels={'x': 'Language', 'y': 'Count'},
             color_discrete_sequence=['#9EE6CF'], opacity=0.9)
fig.update_layout(title='Language Distribution',
                  xaxis_title='', yaxis_title='Count')
st.plotly_chart(fig)


content_df = df[['content', 'contentTranslation', 'languageInEnglish']]
# streamlit show dataframe
st.dataframe(content_df)


st.subheader("Data Preprocessing")
"""
The quality of the data determines the quality of every downstream translation and natural language processing step; thus, it is crucial to meticulously clean the data. The raw texts contain numerous special characters and author explanations. The Ancient Graffiti Project's epigraphic conventions are detailed on their website (http://ancientgraffiti.org/about/main/epigraphic-conventions/). Unlike standard text preprocessing steps for regular English texts, our text preprocessing steps carefully considered the nature of our raw text and the AGP epigraphic conventions. To minimize the impact of these characters and annotations on the topic modeling tasks, we employed the following steps to clean the text:
1. Drop rows with missing values

2. If a row contains "ABC", drop the row

3. Decode the HTML entities into their corresponding characters

4. If "(\:abc)" pattern is found, replace the previous word with the word inside the parentheses

5. remove “?”

6. Replace "((\:abc))" with "abc"

7. Replace "a(bc)" with "abc"

8. Replace "[abc]" and "[[abc]]" to "abc", and "[ab c]" to "ab c", but we leave "[---]" alone

9. Convert texts to lowercase

10. replace "+" with ""

11. replace "\n" with ", " 

12. remove 〈 〉and <> and everything in between 

13. remove 〚〛 and everything in between

14. Text infilling for "[---]" (LatinBERT for Latin and GreekBERT for Greek)

15. Remove remaining special characters

(Note: abc stands for any combination of alphabets)

Steps 1 through 13 were completed using regular expressions. We choose to do text infilling to address the many missing texts in the original text data. After completing basic text preprocessing, we obtained relatively clean texts for text infilling. Since the raw text data are very short and contain a large number of missing characters or incomprehensive letters, most texts are incomprehensible as a result. We hope the text infilling experiment might bring more comprehensibility of the analysis tasks.

For text infilling, we selected a language model to predict missing words. A language model is a statistical model that learns the contextual relationships between words and generates predictions for missing words. Specifically, we chose LatinBERT, developed by Bamman and Burns in 2020. LatinBERT is a fine-tuned version of the BERT model trained on 642.7 million words from a variety of sources spanning the Classical era to the 21st century. Since LatinBERT is trained on a large corpus of Latin text, it is a suitable tool for infilling Latin words. For each text document, if it contains [---], we replaced it with [MASK] and ran the LatinBERT unmasker function to predict the missing content. We chose the highest confidence word and updated the text with the new sequence predicted by the model. We observed that when [MASK] appeared as the last word in a sentence, it was almost always the case that the prediction would be a punctuation. Also, since our texts are very short and contain a lot of missing elements, it is challenging for the language model to accurately predict the missing content.
"""

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

from wordcloud import WordCloud
import streamlit as st
from streamlit import components
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pickle
import plotly.graph_objs as go
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import gensim
from gensim.corpora import Dictionary
import pyLDAvis
import pyLDAvis.gensim
import warnings
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


# Gensim
# vis
warnings.filterwarnings("ignore", category=DeprecationWarning)


with open('data/cleaned_docs.pkl', 'rb') as f:
    cleaned_docs = pickle.load(f)


st.header("Topic Modelling--K Means Clustering")

st.subheader("K means Clustering")
"""
K-means is an unsupervised clustering algorithm that aims to partition the data into K clusters based on the similarity between the data points. The algorithm iteratively assigns each data point to the nearest cluster centroid, and then updates the centroids based on the mean of the points in each cluster.
"""

st.subheader("PCA (Principal Component Analysis)")
"""
PCA is a technique for dimensionality reduction, which means that it allows us to reduce the number of dimensions in our data while retaining most of the variation in the data. This can be very useful for visualizing clusters in high-dimensional data, such as the results of topic modelling or k-means clustering.

In particular, PCA can help us to visualize clusters by reducing the data to two or three dimensions, which can be easily plotted on a graph. This allows us to see the relationships between the different data points and to identify clusters that may not be obvious in higher dimensions. By using PCA to visualize our data, we can gain insights into the structure of our data and identify patterns or trends that may be hidden in higher dimensions.
"""

# --------tfidf vectorizer---------
vectorizer = TfidfVectorizer(
    lowercase=True,
    max_features=100,
    max_df=0.8,             # ignore words that appear in over 80% of the documents
    min_df=5,               # ignore words that appear in less than 5 documents
    ngram_range=(1, 3),    # unigrams, bigrams, trigrams
    stop_words="english"    # remove stopwords
)

vectors = vectorizer.fit_transform(cleaned_docs)

feature_names = vectorizer.get_feature_names_out()

dense = vectors.todense()
denselist = dense.tolist()

all_keywords = []

for description in denselist:
    x = 0
    keywords = []
    for word in description:
        if word > 0:
            keywords.append(feature_names[x])
        x = x+1
    all_keywords.append(keywords)

# kmeans clustering
true_k = 8

model = KMeans(n_clusters=true_k, init="k-means++",
               n_init=20, max_iter=1000,  random_state=42)
model.fit(vectors)

order_centroids = model.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names_out()


# --------PCA---------
# generate cluster indices for each vector
kmean_indices = model.fit_predict(vectors)
# reduce dimensionality to 2D
pca = PCA(n_components=2)
# stores the 2D coordinates of vectors
scatter_plot_points = pca.fit_transform(vectors.toarray())


# -----visualize the PCA result--------
colors = ["#ea5545", "#f46a9b", "#ef9b20", "#edbf33",
          "#ede15b", "#bdcf32", "#87bc45", "#27aeef", "#b33dc6"]

x_axis = [o[0] for o in scatter_plot_points]
y_axis = [o[1] for o in scatter_plot_points]

# create a list of hover text for each point
hover_text = ["Text: {}".format(txt) for txt in cleaned_docs]

# create a trace for each cluster
true_k = 8
data = []
for i in range(true_k):
    trace = go.Scatter(
        x=[x_axis[j]
            for j in range(len(kmean_indices)) if kmean_indices[j] == i],
        y=[y_axis[j]
            for j in range(len(kmean_indices)) if kmean_indices[j] == i],
        mode='markers',
        marker=dict(
            color=colors[i],
            size=10,
            opacity=0.8,
            line=dict(width=0.5, color='white')
        ),
        text=[hover_text[j]
              for j in range(len(kmean_indices)) if kmean_indices[j] == i],
        name=f"Cluster {i}"
    )
    data.append(trace)

# create the layout
layout = go.Layout(
    title='PCA Visualization of Clusters',
    xaxis=dict(title='PC1'),
    yaxis=dict(title='PC2'),
    # plot_bgcolor='white',
)

# plot the figure
fig = go.Figure(data=data, layout=layout)

# Change grid color and axis colors
fig.update_xaxes(showline=True, linewidth=1, linecolor='lightgrey',
                 showgrid=True, gridwidth=1, gridcolor='lightgrey')
fig.update_yaxes(showline=True, linewidth=1, linecolor='lightgrey',
                 showgrid=True, gridwidth=1, gridcolor='lightgrey')
fig.update_yaxes(zeroline=False)
fig.update_xaxes(zeroline=False)

# display the plotly figure using st.plotly_chart()
st.plotly_chart(fig)

"""
Each point represents a vector in the input matrix, and the color of the point indicates which k-means cluster it belongs to. By inspecting the plot, you can get a sense of which vectors are most similar to each other, and which clusters are most distinct from each other.

Based on the word frequencies in each cluster, it's difficult to identify specific topics without more context about the data. However, here are some possible topic labels for each cluster:

Cluster 0: Roman names (references to Lucius, Marcus, Quintus)

Cluster 1: Trade, Economy, and Servitude (references to coins, slave, bread)

Cluster 2: Messages, Greetings, and Informal Language (references to goodbye, text, written, greetings, gods)

Cluster 3: Timekeeping (references to days, july, days kalends)

Cluster 4: Language (references to letters, series, greek, january, ides, liberalis, time, felicio)

Cluster 5: Daily Interactions (references to bread, greetings, happily)

Cluster 6: Social Connections (references to love, greetings, goodbye, antonius, pompeians, live, mark)

Cluster 7: Farewells (references to bye, chloe, paris)
"""

st.header("Topic Modelling--LDA (Latent Dirichlet Allocation)")

"""
K-means is an unsupervised clustering algorithm that aims to partition the data into K clusters based on the similarity between the data points, while LDA is a supervised classification algorithm that aims to find a linear combination of features that maximally separates the classes in the data.

LDA can automatically discover latent topics in a text corpus, and it can also model the probability distribution of words within each topic, which can be used to interpret the meaning of each topic. The algorithm computes the between-class and within-class scatter matrices of the data, and then finds the eigenvectors of the ratio of these matrices that correspond to the largest eigenvalues. The resulting eigenvectors define a subspace that maximally separates the classes, and can be used to project the data onto a lower-dimensional space for classification. LDA is a powerful algorithm that can work well with small to medium-sized datasets, but it has some limitations such as the assumption of Gaussian distributions, the sensitivity to outliers, and the difficulty in handling nonlinear or complex boundaries.
"""
# read in lad model, corpus, id2word
with open('data/corpus.pkl', 'rb') as f:
    corpus = pickle.load(f)

lda_model = gensim.models.ldamodel.LdaModel.load("data/text_model.model")
id2word = Dictionary.load("data/id2word.gensim")

vis = pyLDAvis.gensim.prepare(lda_model, corpus, id2word, mds="mmds", R=30)

# Extract the HTML and JavaScript components of the visualization
html = pyLDAvis.prepared_data_to_html(vis)

# Display the visualization in Streamlit using the components function
components.v1.html(html, width=1400, height=800,
                   scrolling=False)

st.subheader("Word Clouds for LDA Topics")

# show word cloud but with button for display


# Call the code to display word clouds for LDA topics
top_words = []
for i in range(8):
    top_words.append([word[0] for word in lda_model.show_topic(i, topn=10)])

col1, col2, col3 = st.columns(3)
with col1:
    wordcloud = WordCloud(background_color="white", colormap='Set2').generate(
        ' '.join(top_words[0]))
    fig, ax = plt.subplots(figsize=(4, 4), facecolor=None)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title("Topic " + str(0))
    ax.axis("off")
    st.pyplot(fig)
with col2:
    wordcloud = WordCloud(background_color="white", colormap='Set2').generate(
        ' '.join(top_words[1]))
    fig, ax = plt.subplots(figsize=(4, 4), facecolor=None)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title("Topic " + str(1))
    ax.axis("off")
    st.pyplot(fig)
with col3:
    wordcloud = WordCloud(background_color="white", colormap='Set2').generate(
        ' '.join(top_words[2]))
    fig, ax = plt.subplots(figsize=(4, 4), facecolor=None)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title("Topic " + str(2))
    ax.axis("off")
    st.pyplot(fig)

col4, col5, col6 = st.columns(3)
with col4:
    wordcloud = WordCloud(background_color="white", colormap='Set2').generate(
        ' '.join(top_words[3]))
    fig, ax = plt.subplots(figsize=(4, 4), facecolor=None)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title("Topic " + str(3))
    ax.axis("off")
    st.pyplot(fig)
with col5:
    wordcloud = WordCloud(background_color="white", colormap='Set2').generate(
        ' '.join(top_words[4]))
    fig, ax = plt.subplots(figsize=(4, 4), facecolor=None)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title("Topic " + str(4))
    ax.axis("off")
    st.pyplot(fig)
with col6:
    wordcloud = WordCloud(background_color="white", colormap='Set2').generate(
        ' '.join(top_words[5]))
    fig, ax = plt.subplots(figsize=(4, 4), facecolor=None)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title("Topic " + str(5))
    ax.axis("off")
    st.pyplot(fig)

col7, col8, col9 = st.columns(3)
with col7:
    wordcloud = WordCloud(background_color="white", colormap='Set2').generate(
        ' '.join(top_words[6]))
    fig, ax = plt.subplots(figsize=(4, 4), facecolor=None)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title("Topic " + str(6))
    ax.axis("off")
    st.pyplot(fig)
with col8:
    wordcloud = WordCloud(background_color="white", colormap='Set2').generate(
        ' '.join(top_words[7]))
    fig, ax = plt.subplots(figsize=(4, 4), facecolor=None)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title("Topic " + str(7))
    ax.axis("off")
    st.pyplot(fig)
with col9:
    # empty
    st.write("")

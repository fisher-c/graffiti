import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium, folium_static
import osmnx as ox
import geopandas as gpd
import pandas as pd
import streamlit as st
import pydeck as pdk
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

st.title("Cities of Pompeii and Herculaneum")

st.subheader("Pompeii")
"""
Pompeii was an ancient Roman city located in the Campania region of Italy. It was a bustling city with a population of over 10,000 people before it was buried under volcanic ash and pumice during the eruption of Mount Vesuvius in 79 AD. The city was rediscovered in the 18th century and has since been the subject of extensive archaeological research.

Pompeii is known for its well-preserved ruins, including its houses, public buildings, and outdoor spaces. The city is also home to a rich collection of ancient graffiti, which offer glimpses into the thoughts, feelings, and activities of ordinary people in the ancient Roman world. The graffiti range from simple greetings and love declarations to more complex political messages and philosophical musings.

"""

# retrieve the network for Pompeii
G = ox.graph_from_place("Pompeii, Italy", network_type="all")

# convert the graph to a folium map
graph_map = ox.plot_graph_folium(
    G, popup_attribute='name', color="lightcoral", weight=3, opacity=0.7)

# add a tile layer to the folium map
tile_layer = folium.TileLayer('OpenStreetMap').add_to(graph_map)

folium_static(graph_map, width=700)

st.subheader("Herculaneum")

"""
Herculaneum was an ancient Roman town located on the coast of the Bay of Naples, near the base of Mount Vesuvius. Like Pompeii, it was destroyed by the eruption of Mount Vesuvius in 79 AD and was buried under volcanic ash and pumice for centuries. The city is known for its well-preserved ruins, which provide unique insights into the daily lives, beliefs, and customs of its inhabitants.

The Ancient Graffiti Project has documented and catalogued over 2,000 ancient graffiti from Pompeii and Herculaneum, providing a valuable resource for scholars and enthusiasts interested in the social, cultural, and political history of the ancient Roman world.
"""
G = ox.graph_from_place("Herculaneum", network_type="all")
graph_map = ox.plot_graph_folium(
    G, popup_attribute='name', color="lightcoral", weight=3, opacity=0.7)

# add a tile layer to the folium map
tile_layer = folium.TileLayer('OpenStreetMap').add_to(graph_map)

folium_static(graph_map, width=700)

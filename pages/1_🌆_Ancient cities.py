import seaborn as sns
import folium
from streamlit_folium import st_folium, folium_static
import osmnx as ox
import streamlit as st
import pydeck as pdk
import numpy as np
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

@st.cache_resource(show_spinner=False)
def load_graph(place: str):
    # Cache the OSM street network so Streamlit reruns don't keep hitting OSM services.
    return ox.graph_from_place(place, network_type="all")


def _to_popup_text(value):
    # Folium tooltips expect a string; OSMnx edge attributes can be lists/NaNs/etc.
    if value is None:
        return ""
    if isinstance(value, float) and np.isnan(value):
        return ""
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(v) for v in value if v is not None)
    return str(value)


def graph_to_folium_map(
    G,
    *,
    popup_attribute: str = "name",
    popup_label: str = "Street name: ",
    color: str = "lightcoral",
    weight: int = 3,
    opacity: float = 0.7,
    tiles: str = "CartoDB positron",
    zoom_start: int = 16,
):
    # Compatibility layer:
    # - osmnx<2 exposes `ox.plot_graph_folium`
    # - osmnx>=2 removed it, so we render edges ourselves via GeoJSON.
    if hasattr(ox, "plot_graph_folium"):
        # `ox.plot_graph_folium` uses the attribute name as the label. To make it clearer,
        # copy the underlying attribute (e.g. "name") to a new key (e.g. "Street name").
        if popup_attribute != popup_label:
            for _, _, _, data in G.edges(keys=True, data=True):
                if popup_attribute in data and popup_label not in data:
                    data[popup_label] = data[popup_attribute]

        graph_map = ox.plot_graph_folium(
            G,
            popup_attribute=popup_label,
            color=color,
            weight=weight,
            opacity=opacity,
        )
        if tiles:
            folium.TileLayer(tiles).add_to(graph_map)
        return graph_map

    # Convert the network graph to GeoDataFrames (nodes+edges) and draw edges on a Folium map.
    nodes, edges = ox.graph_to_gdfs(
        G, nodes=True, edges=True, node_geometry=True, fill_edge_geometry=True
    )
    center = [float(nodes["y"].mean()), float(nodes["x"].mean())]
    graph_map = folium.Map(location=center, tiles=tiles, zoom_start=zoom_start)

    # Keep only geometry + optional popup attribute to keep the GeoJSON payload small.
    edges = edges[
        ["geometry"] + ([popup_attribute] if popup_attribute in edges.columns else [])
    ].copy()
    tooltip = None
    if popup_attribute in edges.columns:
        edges["_popup"] = edges[popup_attribute].map(_to_popup_text)
        edges.drop(columns=[popup_attribute], inplace=True)
        tooltip = folium.GeoJsonTooltip(
            fields=["_popup"], aliases=[popup_label], sticky=False
        )

    folium.GeoJson(
        edges.to_json(),
        style_function=lambda _: {"color": color, "weight": weight, "opacity": opacity},
        tooltip=tooltip,
        name="Street network",
    ).add_to(graph_map)
    folium.LayerControl().add_to(graph_map)
    return graph_map

st.subheader("Pompeii")
"""
Pompeii was an ancient Roman city located in the Campania region of Italy. It was a bustling city with a population of over 10,000 people before it was buried under volcanic ash and pumice during the eruption of Mount Vesuvius in 79 AD. The city was rediscovered in the 18th century and has since been the subject of extensive archaeological research.

Pompeii is known for its well-preserved ruins, including its houses, public buildings, and outdoor spaces. The city is also home to a rich collection of ancient graffiti, which offer glimpses into the thoughts, feelings, and activities of ordinary people in the ancient Roman world. The graffiti range from simple greetings and love declarations to more complex political messages and philosophical musings.

"""

# retrieve the network for Pompeii
G = load_graph("Pompeii, Italy")

# convert the graph to a folium map
st.caption(
    "This map shows the street network for Pompeii — hover a line to see the street name."
)
graph_map = graph_to_folium_map(
    G, popup_attribute="name", color="lightcoral", weight=3, opacity=0.7
)

folium_static(graph_map, width=700)

st.subheader("Herculaneum")

"""
Herculaneum was an ancient Roman town located on the coast of the Bay of Naples, near the base of Mount Vesuvius. Like Pompeii, it was destroyed by the eruption of Mount Vesuvius in 79 AD and was buried under volcanic ash and pumice for centuries. The city is known for its well-preserved ruins, which provide unique insights into the daily lives, beliefs, and customs of its inhabitants.

The Ancient Graffiti Project has documented and catalogued over 2,000 ancient graffiti from Pompeii and Herculaneum, providing a valuable resource for scholars and enthusiasts interested in the social, cultural, and political history of the ancient Roman world.
"""
G = load_graph("Herculaneum")
st.caption(
    "This map shows the street network for Herculaneum — hover a line to see the street name."
)
graph_map = graph_to_folium_map(
    G, popup_attribute="name", color="lightcoral", weight=3, opacity=0.7
)

folium_static(graph_map, width=700)

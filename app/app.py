import folium
import geopandas

from typing import Tuple, List

import pandas as pd
import streamlit as st

from streamlit_folium import folium_static    
from streamlit.config import _global_development_mode


CHOOSE_DEPARTMENT = 'Choisir un département'


# Loading results per city
results_df = (pd.read_csv('data/04-resultats-par-commune.csv.gz', dtype={'dep_code': str, 'commune_code': str})
                .assign(code=lambda _df: _df['dep_code'] + _df['commune_code'])
                .query('~dep_code.str.startswith("Z")'))

# Computing aggregation per department
results_departments_df = (results_df
 .groupby(['dep_code', 'cand_num_panneau', 'cand_nom', 'cand_prenom'])
 .agg(cand_nb_voix=('cand_nb_voix', 'sum'),
      exprimes_nb=('exprimes_nb', 'sum'))
 .reset_index()
 .rename(columns={'dep_code': 'code'})
 .assign(cand_rapport_exprim=lambda _df: 100 * _df['cand_nb_voix'] / _df['exprimes_nb'])
)

# Computing list of departments
departements = [CHOOSE_DEPARTMENT] + list(results_departments_df['code'].unique())

# Computing list of candidates
candidates = list(results_departments_df['cand_num_panneau'].unique())
candidates_dict = (results_df[['cand_num_panneau', 'cand_prenom', 'cand_nom']]
                    .assign(cand_name=lambda _df: _df['cand_prenom'] + ' ' + _df['cand_nom'])
                    [['cand_num_panneau', 'cand_name']]
                    .drop_duplicates()
                    .set_index('cand_num_panneau')
                    .to_dict()['cand_name'])
candidate_num = candidates[0]

# Loading geojson files
cities_gdf = geopandas.read_file('references/communes-version-simplifiee.geojson')
departements_gdf = geopandas.read_file('references/departements-version-simplifiee.geojson')

# Generate map
def generate_map(data_df: pd.DataFrame, areas_gdf, name: str, var: str,
                 center:List[float]=[46.5, 2.3], zoom_level=5, dark=False):
    if dark:
        # Create a folium map
        m = folium.Map(
            location=center,
            zoom_start=zoom_level,
            tiles='Cartodb dark_matter',
        )
    else:
        # Create a folium map
        m = folium.Map(
            location=center,
            zoom_start=zoom_level,
            tiles=None,
        )
        # No background
        folium.TileLayer("CartoDB positron", name="Light Map", control=False).add_to(m)

    # Tooltip: KO on cities. Probably due to some missing/null values
    # areas_gdf[name] = (areas_gdf
    #                     .merge(data_df, on='code', how='left')
    #                     .assign(tooltip=lambda _df: _df['nom'] + ' : ' + _df[var].apply(lambda x: "{0:.2f} %".format(x)))
    #                     .rename(columns={'tooltip': name})
    #                     [name]
    #                     .fillna('NA')
    # )

    choropleth = folium.Choropleth(
        geo_data=areas_gdf,
        data=data_df,
        columns=['code', var],
        key_on='feature.properties.code',
        fill_color='BuPu',
        fill_opacity=1,
        line_opacity=0.2,
        legend_name=name,
        #bins=bins,
        #reset=True
    ).add_to(m)

    # Tooltip: KO on cities. Probably due to some missing/null values
    # folium.GeoJsonTooltip([name]).add_to(choropleth.geojson)

    return m

    
st.title("Cartographie présidentielle")
st.write("Visualisation & analyse du premier tour de la présidentielle 2022")

with st.sidebar:
    candidate_selector = st.selectbox("Candidat (ordre affichage)", candidates, format_func=lambda x: candidates_dict[x])
    map_level = st.radio("Détail de la carte", ('Département', 'Commune'))
    departements_selector = st.selectbox("Zoom département", departements, disabled=(map_level=='Département'))
    dark_mode = st.radio('Dark mode', ('On', 'Off'), 1)

if departements_selector != CHOOSE_DEPARTMENT and map_level == 'Commune':
    map_center = departements_gdf.query('code == @departements_selector').centroid.map(lambda p: [p.y, p.x]).values[0]
    _area = departements_gdf.query('code == @departements_selector').area.values[0]
    zoom_level = 9 if _area < 0.5 else 8
    m = generate_map(results_df.query('cand_num_panneau == @candidate_selector and dep_code == @departements_selector'),
                     cities_gdf, (lambda x: candidates_dict[x])(candidate_selector), 'cand_rapport_exprim',
                     center=map_center, zoom_level=zoom_level, dark=(dark_mode=='On'))
    folium_static(m)

elif map_level == 'Commune':
    #map_center = departements_gdf.query('code == @departements_selector').centroid.map(lambda p: [p.y, p.x]).values[0]
    #_area = departements_gdf.query('code == @departements_selector').area.values[0]
    #zoom_level = 9 if _area < 0.5 else 8
    m = generate_map(results_df.query('cand_num_panneau == @candidate_selector'),
                     cities_gdf, (lambda x: candidates_dict[x])(candidate_selector), 'cand_rapport_exprim',
                     #center=map_center, zoom_level=zoom_level,
                     dark=(dark_mode=='On'))
    folium_static(m)

elif map_level == 'Département':
    m = generate_map(results_departments_df.query('cand_num_panneau == @candidate_selector'),
                     departements_gdf, (lambda x: candidates_dict[x])(candidate_selector), 'cand_rapport_exprim',
                     dark=(dark_mode=='On'))
    folium_static(m)

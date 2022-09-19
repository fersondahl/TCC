# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 09:56:36 2022

@author: fernando.brito
"""


import pandas as pd


import seaborn as sns
import matplotlib.pyplot as plt
import geopandas
import requests
import shapely
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import numpy as np

import time



mapa = geopandas.read_file(r"https://github.com/fersondahl/dados_uteis/raw/main/Rio%20de%20Janeiro.GEOJSON")


locplan = r"C:\Users\fernando.brito\Downloads\Municipios.xlsx"

geo_df = pd.read_excel(io=locplan)
geo_df['cords'] = list(map(lambda a, b: Point(b, a), geo_df['Latitude'].astype(float), geo_df['Longitude'].astype(float)))

geo_df['chave'] = geo_df.index


mapa = pd.merge(left=mapa, right=geo_df[['Município']], left_index=True, right_index=True, how='left')
munc = ["NITERÓI", "SÃO GONÇALO", "ITABORAÍ", "MARICÁ"]

#%%
with sns.axes_style('dark'):
    # Plotagem do mapa
    
    fig, ax = plt.subplots()
    # Layer RJ
    mapa.query(f"`Município` in {munc}").plot(ax=ax, alpha=0.8,color='slategrey')
    # Coordenadas dos serviços
    plt.plot(list(geo_df.query(f"`Município` in {munc}")['Longitude']), list(geo_df.query(f"`Município` in {munc}")['Latitude']), 'ko')
    
    sub_pontos = geo_df.query(f"`Município` in {munc}").reset_index(drop=True)
    for i in sub_pontos.index.to_list():
        print(i)
        ax.annotate(i+1, np.array(sub_pontos['cords'].loc[i]), horizontalalignment = "right", verticalalignment='top',
                    fontsize=16, color="khaki", weight='bold')
    
    
    
    plt.title("Subconjunto de Cidades - RJ", fontdict={'fontsize': 20, 'horizontalalignment': 'center','verticalalignment': 'bottom'})
    plt.xticks(ticks=[])
    plt.yticks(ticks=[])
    
    
    fig.set_figheight(10, forward=True)
    fig.set_figwidth(15, forward=True)
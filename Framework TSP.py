#%%
import time
import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from haversine import haversine, Unit, haversine_vector
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import geopandas

import shapely
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon

import googlemaps
gmaps = googlemaps.Client(key=os.environ['dist_matrix_key'])

# %%

rj = geopandas.read_file(r"https://github.com/fersondahl-uff/TCC/raw/main/Camada%20RJ.GEOJSON")[["NOME", "geometry"]]

rj['ponto_representativo'] = rj['geometry'].apply(lambda linha: linha.representative_point())

rj['Longitude'] = rj['ponto_representativo'].apply(lambda linha: linha.coords[0][0])
rj['Latitude'] = rj['ponto_representativo'].apply(lambda linha: linha.coords[0][1])

dic_comb = {'origem': [], 'destino': [], 'loc_orig': [], 'loc_dest': []}

geo_df = rj.copy()
geo_df['cords'] = geo_df['Latitude'].astype(str) + ", " + geo_df['Longitude'].astype(str)
geo_df['chave'] = geo_df.index

for i in range(len(geo_df)):
    for j in range(len(geo_df)):
        dic_comb['origem'].append(geo_df['chave'][i])
        dic_comb['destino'].append(geo_df['chave'][j])
        dic_comb['loc_orig'].append(geo_df['cords'][i])
        dic_comb['loc_dest'].append(geo_df['cords'][j])

#### dist - DataFrame de combinação de todas as distâncias das coordenadas entre si
    
dist_df = pd.DataFrame(data=dic_comb)


for col in['loc_orig', 'loc_dest']:
  dist_df[col] = dist_df[col].apply(lambda lin: tuple((list(map(float, lin.split(','))))))

dist_df['Distancia'] = haversine_vector(list(dist_df['loc_orig']), list(dist_df['loc_dest'])).astype(float)

## Tempo de Trajeto através do googlemaps
# dist_df['Distancia'] = list(map(lambda origin, destination: gmaps.distance_matrix(origin,
#                         destination, mode = 'driving'), dist_df['loc_orig'], dist_df['loc_dest']))

# dist_df['Distancia'] = dist_df['Distancia'].apply(lambda linha: linha['rows'][0]['elements'][0]['duration']['value'])

matriz_de_para = dist_df.pivot(values='Distancia', index='origem', columns='destino')

#%%

ciclo = []
subrotas = []
subciclo = []

durac = time.time()


while len(ciclo) != len(geo_df): 
        
    model = pyo.ConcreteModel()
    
    model.vertices = pyo.Var(range(len(matriz_de_para)), range(len(matriz_de_para)), bounds=(0, 1), within=Integers)
    vertices = model.vertices

    model.C1 = pyo.ConstraintList()
    for i in range(len(matriz_de_para)):
        model.C1.add(expr= sum(vertices[i, j] for j in range(len(matriz_de_para))) == 1)  #Restrição (1)
        model.C1.add(expr= sum(vertices[j, i] for j in range(len(matriz_de_para))) == 1) #Restrição (2)
    
    model.C2 = pyo.ConstraintList()
    for i in range(len(matriz_de_para)):
        model.C2.add(expr= vertices[i, i] ==0)    #Imperdir que Xi,i seja igual a 1
    
    model.restS = pyo.ConstraintList()    
    for s in subciclo:
        model.restS.add(expr =sum(vertices[i, j] for i in s for j in s) - len(s) <=  -1) # Restrições DFJ
        
    # print(len(model.restS))


    model.obj = pyo.Objective(expr= sum(
        vertices[i, j]*matriz_de_para[i][j] for i in range(len(geo_df)) for j in range(len(geo_df))), sense=minimize)
    
    
    opt = SolverFactory('glpk')
    opt.solve(model)
    
    result = []
    resultado = []
    
    vet_mult = list(range(len(matriz_de_para)))
    for i in range(len(matriz_de_para)):
        resultado.append(int(sum(pyo.value(vertices[i,j])*vet_mult[j] for j in range(len(matriz_de_para)))))
        
    geo_df['Destino'] = resultado
    
    ciclo = [geo_df['chave'][0]]
    subrotas = []
    arestas = []
    j=0
    
    control = ''
    
    while control != 'done':
    
        for i in range(len(geo_df)):
            ciclo.append(geo_df['Destino'][j])
            arestas.append(geo_df['Destino'][j])
            j=geo_df['Destino'][j]
        
        ciclo = list(dict.fromkeys(ciclo))
        
        subrotas.append(ciclo)
        arest_tot = sum(list(map(lambda elemento: len(elemento), subrotas)))
        dif = list(set(arestas).symmetric_difference(set(list(geo_df['chave']))))
        try:
            j = dif[0]
            ciclo = [dif[0]]
        except IndexError:
            control = 'done'
    
    subciclo +=subrotas

print(f'Otimização concluída em {round(time.time() - durac, 2)} segundos\nDistância total: {round(pyo.value(model.obj), 2)}')

#%%

#### mapa dos trajetos

trajetos_df = geo_df[['chave', 'Latitude', 'Longitude', 'Destino']].rename(
    columns={'chave': 'Origem'})

trajetos_df = pd.merge(left=trajetos_df, right=geo_df[['Longitude', 'Latitude']], left_on='Destino', right_index=True, how='left')


with sns.axes_style('dark'):
    # Plotagem do mapa
    
    fig, ax = plt.subplots()
    # Layer RJ
    rj.plot(ax=ax, alpha=0.8,color='slategrey')
    # Coordenadas dos serviços
    plt.plot(list(geo_df['Longitude']), list(geo_df['Latitude']), 'ko')
    
    # Trajetos
    for i in range(len(trajetos_df)):
        a = [trajetos_df["Longitude_x"][i], trajetos_df["Longitude_y"][i]]
        b = [trajetos_df["Latitude_x"][i], trajetos_df["Latitude_y"][i]]
        plt.plot(a,b, linewidth = 2, linestyle = "-", color = "chocolate")
        
    plt.title("Trajeto Mínimo - RJ", fontdict={'fontsize': 20, 'horizontalalignment': 'center','verticalalignment': 'bottom'})
    plt.xticks(ticks=[])
    plt.yticks(ticks=[])
    
    
    fig.set_figheight(10, forward=True)
    fig.set_figwidth(15, forward=True)
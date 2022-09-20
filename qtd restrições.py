# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 16:26:35 2022

@author: -
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import math

n = 92

resum_var = pd.DataFrame(data=range(3, n + 1)).rename(columns={0: "Nós"})

resum_var['Quantidade Variaveis'] = resum_var["Nós"].apply(lambda linha: math.pow(2, linha) - linha - 2)

resum_var = resum_var.query("`Nós` > 10").reset_index()
resum_var['log_n'] = resum_var['Quantidade Variaveis'].apply(lambda linha: math.log(linha, 10))


with sns.axes_style("dark"):
    fig, ax = plt.subplots()
    
    grafico = sns.lineplot(data=resum_var, x="Nós", y="log_n", ax=ax, linewidth=2, color='cadetblue')
    plt.title("Ordem de restrições por nós", fontdict={"size": 20, 'family': "arial"})
    plt.ylabel("Log (Nº Variáveis)", fontdict={"size": 14, "family": "arial"})
    plt.xlabel("Qtd. de nós", fontdict={"size": 14, "family": "arial"})

    scal_rot = list(ax.get_yticks())
    scal_rot = (scal_rot[1] - scal_rot[0])/20
    valid = 1
    alt = (int(len(list(ax.patches))/2)+1)
    
    sns.despine()
    
    i = 0
    for p in resum_var['log_n']:  ## Rótulos
        height = p
        if (height > 0 and i%10==0): 
            ax.text(resum_var['Nós'][i],
            height + scal_rot,
            round(height, 1),
            ha='center',
            color = 'slategray',
            fontdict={'fontsize': 15, 'family':'arial'},
            weight='bold')
        i += 1 
        
    fig.set_figheight(10, forward=True)
    fig.set_figwidth(20, forward=True)
    
#%%
#INTEGRANTES: Guillermo de la Vega, Matias Naddeo y Francisco Anllo
#En este archivo se corren todos los archivos por separado: las tablas del modelo relacional, los gráficos y los dataframe de las consultas SQL
#Los comentarios de cada uno se encuentran en su propio archivo

import subprocess

def generarTablasModelo():
    subprocess.run(["python", "data_clean.py"], check=True)

def graficos():
    subprocess.run(["python", "graficos.py"], check=True)

def consultas_SQL():
    subprocess.run(["python", "consultas_sql.py"], check=True)

generarTablasModelo()
graficos()
consultas_SQL()

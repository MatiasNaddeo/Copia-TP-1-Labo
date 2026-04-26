#%%
"""
bibliotecas(nro_conabip, nombre, mail, fecha_fundacion, id_departamento)
               pk                                             fk

escuelas(cueanexo, nombre, id_departamento)
             pk                  fk

departamentos(id, nombre, id_provincia)
              pk               fk

provincias(id_provincia, nombre)
                pk

poblacion(id_departamento, edad, cantidad)
                pk          pk

niveles(nivel_educativo)
            pk

tiene(cueanexo,nivel_educativo)
            pk        pk
"""




import pandas as pd
import duckdb as dd
import numpy as  np


escuela=pd.read_excel('TablasOriginales/2025.04.08_padroin_oficial_establecimientos_educativos_die.xlsx',header=12)
bp_crudo=pd.read_csv('TablasOriginales/bibliotecas-populares.csv')
poblacion_bruto=pd.read_excel('TablasOriginales/padron_poblacion.xlsx',header=12)

#TABLA ESCUELAS 
escuela.loc[escuela['Jurisdicción'] == 'Ciudad de Buenos Aires', 'Código de departamento'] = 2000 # fijamos el codigo de depto 2000 para CABA
escuela = escuela[escuela['Común'] == 1] # agarrramos el sub_dataframe con las escuelas de modalidad comun
esc = escuela[['Cueanexo', 'Nombre', 'Código de departamento']] # Tomamos solo estas columnas del original
esc.columns = ["cueanexo", "nombre", "id_departamento"] # cambiamos el nombre de las columnas
esc.to_csv("TablasModelo/escuelas.csv", index=False) # lo pasamos a un csv






#TABLA BIBLIOTECA
bp=bp_crudo[['nro_conabip','nombre','mail','fecha_fundacion','id_departamento','departamento','provincia']] # agarramos estas columnas 
bp = bp.copy() 
def f(x): # funcion para que solo aparezca gmail,hotmail y No algo@gmail.com o algo@hotmail.com sirve para el punto 4)
    if pd.isna(x):
        return np.nan
    if '@' in x:
        return x.split('@')[1].split('.')[0]     # separamos por @ y nos quedamos con la parte derecha y luego separamos por el punto y nos quedamos con lo del lado izquierdo  
      
bp['mail']=bp[['mail']].applymap(f) # se la aplicamos a la columna mail
bp['id_departamento']=bp['id_departamento'].fillna(0).astype(int) # cambiamos los nan por 0 y convertimos todo a int para cambiar los id equivocados

bp['original']=bp['id_departamento'] # esto es para chequear cuantos modificamos despues, principalmente para lo de gqm
def corregir_id(x): # funcion que toma la moda(valor que mas se repite) y se lo aplica a todos los que sean distintos 
    moda=x['id_departamento'].mode()[0]
    x.loc[:,'id_departamento']=moda
    return x
  
bp=bp.groupby(['departamento','provincia'],group_keys=False).apply(corregir_id) 
# agrupamos por id y provincia para cambiar los de mismo departamento y mantener los que estan en distintas provincias
cant_cambios=(bp['id_departamento']!=bp['original']).sum() # contamos la cantidad de cambios 
print(cant_cambios)
bp=bp[['nro_conabip','nombre','fecha_fundacion','mail','id_departamento']] # tomamos estas columnas 
bp.to_csv("TablasModelo/bibliotecas.csv", index=False) # pasamos un csv 



#TABLA DEPARTAMENTO
#funcion que crea a partir de la tabla poblacion la tabla de dapratamentos, tomando tambien el id de provincia 
deptos=[]
estaCABA=False
for _, row in poblacion_bruto.iterrows():
    celdaB = row[1]   # columna B
    celdaC = row[2]   # columna C
    # Caso 1: fila de AREA
    if isinstance(celdaB, str) and isinstance(celdaC, str) and "AREA" in celdaB:
        id_provincia = str(int(celdaB.split()[-1][0:2]))
        if celdaC.startswith("Comuna"):
            if not estaCABA:
                deptos.append(["2000", "Ciudad Autónoma de Buenos Aires", id_provincia])          # código para Ciudad Autónoma de Buenos Aires
                estaCABA=True
        else:
            partes = celdaB.split()
            codigo = partes[-1]              # último fragmento
            departamento = celdaC             # nombre del departamento
            deptos.append([codigo, departamento, id_provincia])
    

depto = pd.DataFrame(deptos, columns=["id", "nombre", "id_provincia"]) # pasamos lo obtenido en la funcion a un dataframe 
depto['id']=depto['id'].astype(int) # ponemos en tipo int
depto['id']=depto['id'].replace(94015,94014) # reemplazamos valor de id de Usuahia que estaba erroneo
depto['id']=depto['id'].replace(94008,94007) # reemplazamos valor de id de Rio Grande que estaba erroneo
depto.to_csv("TablasModelo/departamentos.csv", index=False) # pasamos a un csv 

#TABLA PROVINCIA
provincia=bp_crudo[['id_provincia','provincia']].drop_duplicates() # creamos provincias a partir de bibliotecas y eliminamos los duplicados
provincia.columns = ["id_provincia", "nombre"] # cambiamos nomnre de columna
provincia.to_csv("TablasModelo/provincias.csv", index=False) #pasamos a csv 


#TABLA DE RELACION TIENE
#################################################
# lista con los nombres de las columnas que indican los niveles educativos
niveles = ['Nivel inicial - Jardín maternal','Nivel inicial - Jardín de infantes','Primario','Secundario','Secundario - INET','SNU','SNU - INET','SNU - Cursos']

# recorrer el DataFrame y armar la lista de registros deseados
registros = []
for _, row in escuela.iterrows():
    cueanexo = row["Cueanexo"] # tomamos por fila el valor de la columna Cuanexo
    for nivel in niveles: # recorremos la lista
        if row[nivel] == 1:  # si para ese cueanexo aparece un 1 en el nivel educativo
            registros.append({"cueanexo": cueanexo, "nivel_educativo": nivel}) # lo guardamos en un diccionario con el valor educativo
# Crear un nuevo DataFrame con los registros generados
tiene = pd.DataFrame(registros) # armo el dataframe con el diccionario 
#####################################
tiene.columns = ["cueanexo","nivel_educativo"] # cambiamos nombres de las columnas 
tiene.to_csv("TablasModelo/tiene.csv", index=False) # pasamos a un csv






# TABLA NIVELES
###########################################################
#selecionamos el nivel educativo y ordenamos por eso mismo 
tabla_niveles="""
     SELECT nivel_educativo  
     FROM tiene                   
     GROUP BY nivel_educativo
     ORDER BY nivel_educativo ASC 
"""
niveles=dd.sql(tabla_niveles).df() 
###############################################
niveles.to_csv("TablasModelo/niveles.csv", index=False) # pasamos a un csv





#TABLA POBLACION
###############################################################
r = []
codigo = ""
departamento = ""
miniTabla = False
for _, row in poblacion_bruto.iterrows(): # recorremos las filas 
    celdaB = row[1]   # columna B
    celdaC = row[2]   # columna C

    # caso 1: fila de AREA 
    if isinstance(celdaB, str) and "AREA" in celdaB:  # chequea el valor sea string y despues que diga AREA para sacar id y nombre del depto
        partes = celdaB.split()                       # separo AREA del id
        codigo = partes[-1]              # agarro el codigo 
        departamento = celdaC       # agarro el nombre del departamento o nada 
        miniTabla = False           # mantengo este valor para que no empiece a calcular la cantidades
    # caso 2: inicio de mini-tabla
    elif isinstance(celdaB, str) and celdaB == "Edad": # si el valor es string y EDAD entonces va a empezar a tomar los valores de las minitablas por departamento
        miniTabla = True # actualiza el valor 
    elif isinstance(celdaB, str) and "RESUMEN" in celdaB: # si encuentra la palabra RESUMEN termina el bucle para sumar los totales
        break  
    # caso 3: dentro de la tabla, filas con datos
    elif miniTabla and isinstance(celdaB, (int, float)) and isinstance(celdaC, (int, float)): # empieza a sumar los valores chequeando que los tipos de datos sean correctos
        r.append([codigo,departamento,int(celdaB),int(celdaC)]) # agrego al diccionario los valores del id,del nombre del depto y la edad, cantidad
    # caso 4: cualquier otra fila (por ejemplo encabezados posteriores o "Total")
    else:
        # si detecta "Total" cierra la tabla:
        if isinstance(celdaB, str) and celdaB == "Total":
            miniTabla = False
df = pd.DataFrame(r, columns=['Codigo','Departamento','Edad','Casos']) # creamos el dataframe


#CONSULTA PARA JUNTAR LAS COMUNAS Y PONER Ciudad Autónoma de Buenos Aires, haciendolo por separado y despues juntando los casos que son comuna y todos lo que no
consulta_sql="""
        SELECT Codigo, Edad, SUM(Cantidad) as Cantidad
FROM(
   SELECT '2000' AS Codigo, Edad,SUM(Casos) AS Cantidad
   FROM df
   WHERE Departamento LIKE 'Comuna%'
   GROUP BY Edad
   
UNION ALL 
 
   SELECT Codigo,Edad,Casos as Cantidad
   FROM df 
   WHERE Departamento NOT LIKE 'Comuna%'
 )
 GROUP BY Codigo,Edad
 ORDER BY Codigo ASC , Edad
 """
poblacion = dd.sql(consulta_sql).df()

#######################################################
poblacion.columns = ["id_departamento", "edad", "cantidad"] # cambiamos nombres de las columnas
poblacion['id_departamento'] = poblacion['id_departamento'].astype(int) # cambiamos el tipo de dato para cambiar los valores de Usuahia y Rio Grande

poblacion['id_departamento']=poblacion['id_departamento'].replace(94015,94014) #cambiamos Usuahia
poblacion['id_departamento']=poblacion['id_departamento'].replace(94008,94007) # cambiamos Rio Grande
poblacion.to_csv("TablasModelo/poblacion.csv", index=False) # lo pasamos a csv

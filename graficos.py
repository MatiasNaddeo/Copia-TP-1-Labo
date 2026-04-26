#%%
import pandas as pd
import duckdb as dd
import matplotlib.pyplot as plt
import seaborn as sns


escuelas = pd.read_csv('D:/BIBLIOTECAS/Escritorio/Fran/Python/escuelas.csv')
departamentos = pd.read_csv('D:/BIBLIOTECAS/Escritorio/Fran/Python/departamentos.csv')
bibliotecas = pd.read_csv('D:/BIBLIOTECAS/Escritorio/Fran/Python/bibliotecas.csv')
niveles = pd.read_csv('D:/BIBLIOTECAS/Escritorio/Fran/Python/tiene.csv')
poblacion = pd.read_csv('D:/BIBLIOTECAS/Escritorio/Fran/Python/poblacion.csv')
provincias = pd.read_csv('D:/BIBLIOTECAS/Escritorio/Fran/Python/provincias.csv')









#region punto 1
####### CODIGO 1 ######
codigo1 = """SELECT p.nombre AS nombre, COUNT(b.nro_conabip) AS N_bibliotecas
             FROM  departamentos d
             LEFT OUTER JOIN bibliotecas b ON d.id=b.id_departamento
             INNER JOIN provincias p ON d.id_provincia = p.id_provincia
             GROUP BY p.nombre
             ORDER BY N_bibliotecas ASC
"""

bib_p_depto=dd.sql(codigo1).df()
bib_p_depto['nombre']= bib_p_depto['nombre'].replace('Ciudad Autónoma de Buenos Aires','CABA')


#####GRAFICO 1######
fig, ax = plt.subplots() 
ax.barh(data=bib_p_depto,y='nombre', width='N_bibliotecas')
ax.set_title('Bibliotecas por Provincia')
ax.set_ylabel('Provincias', fontsize='medium')         
ax.set_xlabel('N° de Bibliotecas Públicas', fontsize='medium')
ax.bar_label(ax.containers[0], padding=2,fontsize=8) 
plt.show()
#endregion






















#region punto 2
######## CODIGO  2 ########

#sumamos la población de cada nivel educativo y agrupamos por cada departamento
sub_consulta1_sql=""" SELECT prov.nombre,d.id, d.nombre, 
                        SUM(CASE WHEN p.edad >= 0 and p.edad <= 5 THEN p.cantidad ELSE 0 END) as pob_jardin,
                        SUM(CASE WHEN p.edad >= 6 and p.edad <= 12 THEN p.cantidad ELSE 0 END) as pob_primario,
                        SUM(CASE WHEN p.edad >= 13 and p.edad <= 18 THEN p.cantidad ELSE 0 END) as pob_secundario,
                        SUM(CASE WHEN p.edad >= 19 and p.edad <= 75 THEN p.cantidad ELSE 0 END) as pob_SNU,
                      FROM poblacion as p
                      INNER JOIN departamentos as d ON p.id_departamento = d.id
                      INNER JOIN provincias as prov ON prov.id_provincia = d.id_provincia
                      GROUP BY prov.nombre, d.nombre, d.id
                      ORDER BY d.nombre ASC
"""
res1=dd.sql(sub_consulta1_sql).df()

#contamos la cantidad de establecimientos educativos de cada nivel de cada departamento
sub_consulta1_1_sql=""" SELECT t.id_departamento,
                            SUM(CASE WHEN t.nivel_educativo LIKE 'Nivel%' THEN 1 ELSE 0 END) as jardin,
                            SUM(CASE WHEN t.nivel_educativo LIKE 'Primario' THEN 1 ELSE 0 END) as Primario,
                            SUM(CASE WHEN t.nivel_educativo LIKE 'Secundario%' THEN 1 ELSE 0 END) as Secundario,
                            SUM(CASE WHEN t.nivel_educativo LIKE 'SNU%' THEN 1 ELSE 0 END) as SNU,
                        FROM (SELECT *
                              FROM escuelas as e
                              INNER JOIN niveles as ti ON e.cueanexo = ti.cueanexo) as t
                        GROUP BY id_departamento 
                        ORDER BY id_departamento ASC
"""
res2 = dd.sql(sub_consulta1_1_sql).df()

#unimos ambos datos en un único data frame para luego graficarlo
consulta1_sql="""SELECT res1.nombre as Provincia, res1.nombre_1 as Departamento, res2.jardin as Jardines, res1.pob_jardin as Poblacion_jardin,
                res2.Primario as Primarios, res1.pob_primario as Poblacion_primario, res2.Secundario as Secundarios, res1.pob_secundario as Poblacion_secundario,
                res2.SNU, res1.pob_SNU as Poblacion_snu
                FROM res1 
                LEFT OUTER JOIN res2 ON res1.id = res2.id_departamento
                GROUP BY res1.nombre, res1.nombre_1, res2.jardin, res1.pob_jardin, res2.Primario, res1.pob_primario, res2.Secundario, res1.pob_secundario, res2.SNU, res1.pob_SNU
                ORDER BY res1.nombre ASC, res2.Primario DESC
"""
res_final_consulta1=dd.sql(consulta1_sql).df()

data=res_final_consulta1

####### GRAFICOS 2 ######
fig, ax = plt.subplots() 
plt.rcParams['font.family'] = 'sans-serif'           
ax.scatter(data = data,  x='Poblacion_jardin', y='Jardines',s=1,color='green')
ax.set_title('Población vs Jardines')
ax.set_xlabel('Población en edad de Jardín', fontsize='medium')         
ax.set_ylabel('Cantidad de Jardines', fontsize='medium')
ax.set_xscale('log')
ax.set_yscale('log')
plt.show()

fig, ax = plt.subplots() 
plt.rcParams['font.family'] = 'sans-serif'           
ax.scatter(data = data,  x='Poblacion_primario', y='Primarios',s=1,color='red')
ax.set_title('Población vs Primarias')
ax.set_xlabel('Población en edad de Primaria', fontsize='medium')         
ax.set_ylabel('Cantidad de Primarias', fontsize='medium')
ax.set_xscale('log')
ax.set_yscale('log')
plt.show()

fig, ax = plt.subplots() 
plt.rcParams['font.family'] = 'sans-serif'           
ax.scatter(data = data,  x='Poblacion_secundario', y='Secundarios',s=1,color='blue')
ax.set_title('Población vs Secundarios')
ax.set_xlabel('Población en edad de Secundario', fontsize='medium')         
ax.set_ylabel('Cantidad de Secundarios', fontsize='medium')
ax.set_xscale('log')
ax.set_yscale('log')
plt.show()

fig, ax = plt.subplots() 
plt.rcParams['font.family'] = 'sans-serif'           
ax.scatter(data = data,  x='Poblacion_snu', y='SNU',s=1,color='purple')
ax.set_title('Población vs SNU')
ax.set_xlabel('Población en edad de SNU', fontsize='medium')         
ax.set_ylabel('Cantidad de SNU', fontsize='medium')
ax.set_xscale('log')
ax.set_yscale('log')
plt.show()


###### GRAFICO 2 PERO TODOS JUNTOS #######
fig, ax = plt.subplots()
plt.rcParams['font.family'] = 'sans-serif'
niveles= {'Jardines': ('Poblacion_jardin', 'Jardines', 'green'),
'Primarios': ('Poblacion_primario', 'Primarios', 'red'),
'Secundarios':('Poblacion_secundario', 'Secundarios','blue'),
'SNU':('Poblacion_snu', 'SNU', 'purple')}
for nombre, (xcol, ycol, color) in niveles.items():
    ax.scatter(data=data, x=xcol, y=ycol, s=1, color=color, label=nombre)

ax.set_title('Población vs Instituciones')
ax.set_xlabel('Población en edad escolar', fontsize='medium')         
ax.set_ylabel('Cantidad de instituciones', fontsize='medium')
ax.set_xscale('log')
ax.set_yscale('log')
ax.legend()
plt.show()


#endregion











#region punto 3
####### CODIGO 3 #######
#Es el mismo código de la consulta 3 de SQL:
poblaciontotal_sql = """ SELECT id_departamento, SUM(poblacion.cantidad) as poblacion_total
                         FROM departamentos
                         INNER JOIN poblacion ON poblacion.id_departamento = departamentos.id 
                         GROUP BY id_departamento
                         ORDER BY poblacion_total DESC
"""

pobtotal=dd.sql(poblaciontotal_sql).df()

escuelastotales_sql = """ SELECT departamentos.id, COUNT(escuelas.cueanexo) AS establecimientos_educativos
                          FROM departamentos
                          LEFT OUTER JOIN escuelas ON escuelas.id_departamento = departamentos.id
                          GROUP BY departamentos.id
                          ORDER BY establecimientos_educativos ASC
"""
esctotales=dd.sql(escuelastotales_sql).df()

bibliotecastotales_sql = """ SELECT departamentos.id, COUNT(bibliotecas.nro_conabip) AS bibliotecas_populares
                             FROM departamentos
                             LEFT OUTER JOIN bibliotecas ON bibliotecas.id_departamento = departamentos.id
                             GROUP BY departamentos.id
                             ORDER BY bibliotecas_populares ASC
"""

bibtotales=dd.sql(bibliotecastotales_sql).df()



consulta3_sql = """ SELECT departamentos.nombre AS Departamento, provincias.nombre AS Provincia, pobtotal.poblacion_total, esctotales.establecimientos_educativos, bibtotales.bibliotecas_populares 
                    FROM departamentos
                    INNER JOIN pobtotal ON pobtotal.id_departamento = departamentos.id
                    LEFT OUTER JOIN esctotales ON esctotales.id = departamentos.id
                    LEFT OUTER JOIN bibtotales ON bibtotales.id = departamentos.id
                    INNER JOIN provincias ON provincias.id_provincia = departamentos.id_provincia
                    ORDER BY esctotales.establecimientos_educativos DESC, bibtotales.bibliotecas_populares DESC, Provincia ASC, Departamento ASC 
"""
res_final_consulta3=dd.sql(consulta3_sql).df()


######### GRAFICO 3 ########
region3=res_final_consulta3
region3['Provincia']= region3['Provincia'].replace('Ciudad Autónoma de Buenos Aires','CABA')

orden_provincias = region3.groupby('Provincia')['establecimientos_educativos'].median().sort_values().index


plt.figure(figsize=(15, 6))
sns.boxplot(
    data=region3,
    x='Provincia',
    y='establecimientos_educativos',
    order=orden_provincias  # ordenamos los boxplots según la mediana
)
plt.xticks(rotation=45, ha='right')
plt.title('EE por Provincia')
plt.xlabel('Provincia')
plt.ylabel('Cantidad de EE')
plt.yscale('log')
plt.tight_layout()
plt.show()


#endregion















#region punto 4

######## CODIGO 4 ######
pob_p_depto = """ SELECT id_departamento, SUM(cantidad) AS totalP 
                FROM poblacion 
                GROUP BY id_departamento 
                ORDER BY totalP DESC
"""
pob_p_depto = dd.sql(pob_p_depto).df()

esc_p_depto = """ SELECT id_departamento, COUNT(*) AS totalE 
                  FROM escuelas 
                  GROUP BY id_departamento 
                  ORDER BY totalE DESC
"""
esc_p_depto=dd.sql(esc_p_depto).df()

bib_p_depto = """ SELECT id_departamento, COUNT(*) AS totalB 
                  FROM bibliotecas 
                  GROUP BY id_departamento 
                  ORDER BY totalB DESC
"""
bib_p_depto=dd.sql(bib_p_depto).df()

b_e = """ SELECT p.id_departamento, p.totalP, e.totalE, b.totalB 
          FROM pob_p_depto p
          LEFT OUTER JOIN esc_p_depto e ON p.id_departamento = e.id_departamento
          LEFT OUTER JOIN bib_p_depto b ON p.id_departamento = b.id_departamento
"""
b_e = dd.sql(b_e).df()

relacion = """ SELECT d.nombre, b_e.id_departamento, ROUND((b_e.totalB*1000)/b_e.totalP, 4) AS bibliotecas_cada_1000_habitantes, 
               ROUND((b_e.totalE*1000)/b_e.totalP, 4) AS escuelas_cada_1000_habitantes 
               FROM b_e JOIN departamentos d ON b_e.id_departamento = d.id
               ORDER BY escuelas_cada_1000_habitantes DESC
"""
relacion=dd.sql(relacion).df()




#######  GRAFICO 4 #######

fig, ax = plt.subplots() 
plt.rcParams['font.family'] = 'sans-serif'           
ax.scatter(data = relacion, x='bibliotecas_cada_1000_habitantes', y='escuelas_cada_1000_habitantes',s=2,color='darkBlue')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_title('Cantidad de Bibliotecas vs Cantidad de Escuelas cada 1000 habitantes')
ax.set_xlabel('Bibliotecas', fontsize='medium')         
ax.set_ylabel('Escuelas', fontsize='medium')
plt.show()

#endregion 


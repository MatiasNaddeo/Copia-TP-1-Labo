#%%
import pandas as pd
import duckdb as dd

escuelas = pd.read_csv('TablasModelo/escuelas.csv')
departamentos = pd.read_csv('TablasModelo/departamentos.csv')
bibliotecas = pd.read_csv('TablasModelo/bibliotecas.csv')
niveles = pd.read_csv('TablasModelo/tiene.csv')
poblacion = pd.read_csv('TablasModelo/poblacion.csv')
provincias = pd.read_csv('TablasModelo/provincias.csv')
"""
                                 TABLAS

bibliotecas (nro_conabip, nombre, mail, fecha_fundacion, id_departamento)
                pk                                             fk

 (cueanexo, nombre, id_departamento)
              pk                  fk

departamentos (id, nombre, id_provincia)
               pk               fk

provincias (id_provincia, nombre)
                 pk

poblacion (id_departamento, edad, cantidad)
                 pk          pk

niveles(nivel_educativo)
            pk

tiene(cueanexo,nivel_educativo)
            pk        pk

"""


############################################# CONSULTAS SQL #############################################33
#1)

#sumamos la población de cada nivel educativo y agrupamos por cada departament
pob_nivel_educativo_sql = """ SELECT prov.nombre,d.id, d.nombre,
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
res1 = dd.sql(pob_nivel_educativo_sql).df()

#contamos la cantidad de establecimientos educativos de cada nivel de cada departamento
cant_niveles_educativos_sql = """ SELECT t.id_departamento,
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

res2 = dd.sql(cant_niveles_educativos_sql).df()


consulta1_sql = """ SELECT res1.nombre as Provincia, res1.nombre_1 as Departamento, res2.jardin as Jardines, res1.pob_jardin as Poblacion_jardin,
                    res2.Primario as Primarios, res1.pob_primario as Poblacion_primario, res2.Secundario as Secundarios, res1.pob_secundario as Poblacion_secundario,
                    res2.SNU, res1.pob_SNU as Poblacion_snu
                    FROM res1 
                    LEFT OUTER JOIN res2 ON res1.id = res2.id_departamento
                    GROUP BY res1.nombre, res1.nombre_1, res2.jardin, res1.pob_jardin, res2.Primario, res1.pob_primario, res2.Secundario, res1.pob_secundario, res2.SNU, res1.pob_SNU
                    ORDER BY res1.nombre ASC, res2.Primario DESC
"""
res_final_consulta1=dd.sql(consulta1_sql).df()
print(res_final_consulta1)
res_final_consulta1.to_csv('Resultados_sql/resultado_consulta1.csv')

#2)
#contamos la cantidad de bibliotecas de cada departamento siempre y cuando su fecha sea mayor a 1950.
#hacemos left outer join para también considerar aquellos departamentos que no tengan bibliotecas

consulta2_sql = """ SELECT t.Provincia, t.Departamento, t.bibliotecas_públicas_post_1950
                       FROM (SELECT id, departamentos.nombre AS Departamento, provincias.nombre AS Provincia,  COUNT(CASE WHEN bibliotecas.fecha_fundacion >= '1950-01-01' THEN 1 ELSE NULL END) as bibliotecas_públicas_post_1950
                             FROM departamentos 
                             LEFT OUTER JOIN provincias ON provincias.id_provincia = departamentos.id_provincia
                             LEFT OUTER JOIN bibliotecas ON departamentos.id = bibliotecas.id_departamento
                             GROUP BY id, Departamento, Provincia
                             ORDER BY Provincia ASC, bibliotecas_públicas_post_1950 DESC) as t
"""
res_final_consulta2=dd.sql(consulta2_sql).df()
print(res_final_consulta2)
res_final_consulta2.to_csv('Resultados_sql/resultado_consulta2.csv')


#3)
#hacemos inner join, pues ya sabemos que todos los departamentos aparecen en la tabla de población
poblaciontotal_sql = """ SELECT id_departamento, SUM(poblacion.cantidad) as poblacion_total
                         FROM departamentos
                         INNER JOIN poblacion ON poblacion.id_departamento = departamentos.id 
                         GROUP BY id_departamento
                         ORDER BY poblacion_total DESC

"""

pobtotal=dd.sql(poblaciontotal_sql).df()

#hacemos left outer join para no dejar afuera aquellos departamentos que no tengan ni escuelas ni bibliotecas
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
print(res_final_consulta3)
res_final_consulta3.to_csv('Resultados_sql/resultado_consulta3.csv')



#4)
#contamos la cantidad de mails de cada departamento, y los agrupamos
contarmails_sql = """SELECT t.id_departamento, t.mail, COUNT(*) as Total
                       FROM (SELECT *
                             FROM bibliotecas as b 
                             INNER JOIN departamentos as d ON d.id = b.id_departamento
                             WHERE b.mail NOT LIKE 'Nan') as t
                       GROUP BY t.id_departamento, t.mail
                       ORDER BY t.id_departamento ASC
"""
res_sub_consulta4=dd.sql(contarmails_sql).df()

#nos quedamos con el dominio del mail que sea igual al dominio más frecuente por cada departamento
consulta4_sql = """SELECT prov.nombre as Provincias, d.nombre as Departamento, r.mail as Dominio_Mas_Frecuente
                   FROM res_sub_consulta4 as r
                   INNER JOIN departamentos as d ON r.id_departamento = d.id
                   INNER JOIN provincias as prov ON prov.id_provincia = d.id_provincia 
                   WHERE r.Total = (SELECT MAX(Total)
                                    FROM res_sub_consulta4 as r
                                    WHERE r.id_departamento = d.id)
                   GROUP BY d.nombre, prov.nombre, r.mail
                   ORDER BY prov.nombre ASC
"""
res_final_consulta4=dd.sql(consulta4_sql).df()
print(res_final_consulta4)
res_final_consulta4.to_csv('Resultados_sql/resultado_consulta4.csv')

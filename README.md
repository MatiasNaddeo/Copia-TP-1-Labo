# Análisis de Datos Educativos y Culturales

Este proyecto busca entender mejor la distribución geográfica y estadística de los **establecimientos educativos**, **pibliotecas populares** y la **población** en Argentina. A partir de tres fuentes oficiales, se limpian y procesan los datos, se arman visualizaciones claras, y se hacen consultas SQL para sacar conclusiones.

---

## ¿Cómo empezar?

1. Necesitás tener Python 3 instalado.
2. En la terminal podés correr cualquiera de estos comandos, según lo que necesites:

```bash
python main.py
```

```bash
python data-clean.py
```

```bash
python graficos.py
```

```bash
python consultas_sql.py
```

`main.py` ya se encarga de ejecutar los tres pasos, uno tras otro:

1. Limpieza de datos y armado del modelo (`data-clean.py`)
2. Visualización gráfica (`graficos.py`)
3. Consultas SQL para el análisis final (`consultas_sql.py`)

---

## Estructura del proyecto
```
📁 TP-Labo/
├── main.py
├── data-clean.py
├── graficos.py
├── consultas_sql.py
├── plots/
├── TablasOriginales/
├── TablasModelo/
├── Resultados_sql/
├── Anexo/
└── README.md
```

### `main.py`

Corre todo de una: limpia los datos, hace los gráficos y ejecuta las consultas.

### `data-clean.py`

Toma los datos crudos de `TablasOriginales/` y deja todo listo en `TablasModelo/`.

### `graficos.py`

Usa las tablas limpias para mostrar gráficos que ayudan a interpretar los datos.

### `consultas_sql.py`

Hace las consultas sobre las tablas del modelo y guarda los resultados en `Resultados_sql/`.

---

## Carpetas importantes

### `TablasOriginales/`

Bases de datos sin procesar, todas de acceso público:

* `2025.04.08_padroin_oficial_establecimientos_educativos_die.xlsx`
* `bibliotecas-populares.csv`
* `padron_poblacion.xlsx`

### `TablasModelo/`

Contiene las tablas ya limpias y adaptadas al modelo relacional:

* `bibliotecas.csv`
* `departamentos.csv`
* `escuelas.csv`
* `niveles.csv`
* `poblacion.csv`
* `provincias.csv`
* `tiene.csv`

### `Resultados_sql/`

Ahí van los CSV generados al ejecutar `consultas_sql.py`.

### `plots/`

Imágenes de los gráficos generados por el script de visualización.

### `Anexo/`

Material extra que se usó durante el trabajo pero que no forma parte del análisis final.

---

## Requisitos técnicos

* Python 3.8 o más nuevo
* Bibliotecas necesarias: `pandas`, `numpy`, `matplotlib` (y `sqlite3`, que ya viene con Python)

---

## Autoría y licencia

Trabajo práctico con fines educativos. Todo el contenido se basa en datos oficiales y públicos. Es libre de licencia para fines educativos.

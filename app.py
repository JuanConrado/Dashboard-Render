import geopandas as gpd
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
import mapclassify
import json
import pathlib

# =========================
# 1. Cargar datos geográficos
# =========================
try:
    gdf = gpd.read_file("outputs/tasas_hogares_dep.geojson")
except Exception as e:
    print("⚠️ No se encontró el archivo GeoJSON. Verifica que exista en outputs/")
    raise e

# Asegurar sistema de coordenadas (para visualización web)
gdf = gdf.to_crs(4326)

# =========================
# 2. Validar columnas
# =========================
# Buscar columna con los porcentajes de pobreza
col_pobreza = next((c for c in gdf.columns if "pobreza" in c.lower()), None)
if not col_pobreza:
    raise ValueError(f"No se encontró una columna de pobreza en el GeoJSON. Columnas disponibles: {list(gdf.columns)}")

# Buscar nombre del departamento
col_nom = next((c for c in gdf.columns if "nmbr" in c.lower() or "nombre" in c.lower()), "COD_DPTO")

# Limpiar datos nulos
gdf[col_pobreza] = pd.to_numeric(gdf[col_pobreza], errors="coerce")
gdf = gdf.dropna(subset=[col_pobreza])

# =========================
# 3. Crear la app Dash
# =========================
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H3("Taller · Pobreza de hogares (%) — Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.Label("Clasificación"),
            dcc.Dropdown(
                id="scheme",
                options=[
                    {"label": "Quantiles", "value": "quantiles"},
                    {"label": "Jenks (Natural Breaks)", "value": "jenks"},
                    {"label": "Equal Interval", "value": "equalinterval"}
                ],
                value="quantiles"
            )
        ], style={"width": "30%", "display": "inline-block", "marginRight": "2%"}),

        html.Div([
            html.Label("k (clases)"),
            dcc.Slider(id="k", min=3, max=7, step=1, value=5, marks={i: str(i) for i in range(3, 8)})
        ], style={"width": "30%", "display": "inline-block", "marginRight": "2%"}),

        html.Div([
            html.Label("Paleta"),
            dcc.Dropdown(
                id="palette",
                options=[{"label": p, "value": p} for p in ["YlOrRd", "BuGn", "Oranges", "Greens", "Purples"]],
                value="BuGn"
            )
        ], style={"width": "30%", "display": "inline-block"})
    ], style={"padding": "20px"}),

    dcc.Graph(id="mapa"),

    html.Div([
        html.Div([
            html.H5("Top 5 (%)"),
            dash_table.DataTable(
                id="top5",
                columns=[{"name": i, "id": i} for i in [col_nom, "COD_DPTO", col_pobreza]],
                style_table={"overflowX": "auto"}
            )
        ], style={"width": "45%", "display": "inline-block"}),

        html.Div([
            html.H5("Bottom 5 (%)"),
            dash_table.DataTable(
                id="bottom5",
                columns=[{"name": i, "id": i} for i in [col_nom, "COD_DPTO", col_pobreza]],
                style_table={"overflowX": "auto"}
            )
        ], style={"width": "45%", "display": "inline-block", "float": "right"})
    ])
])

# =========================
# 4. Callbacks interactivos
# =========================
@app.callback(
    Output("mapa", "figure"),
    Output("top5", "data"),
    Output("bottom5", "data"),
    Input("scheme", "value"),
    Input("k", "value"),
    Input("palette", "value")
)
def actualizar_mapa(scheme, k, palette):
    # Calcular intervalos
    try:
        classifier = mapclassify.classify(gdf[col_pobreza].values, scheme=scheme, k=k)
        gdf["class"] = classifier.yb
    except Exception:
        gdf["class"] = 0

    # Crear mapa
    fig = px.choropleth_mapbox(
        gdf,
        geojson=json.loads(gdf.to_json()),
        locations=gdf.index,
        color=col_pobreza,
        color_continuous_scale=palette,
        mapbox_style="carto-positron",
        center={"lat": 4.6, "lon": -74.1},
        zoom=4.3,
        opacity=0.85,
        hover_data=[col_nom, "COD_DPTO", col_pobreza]
    )

    fig.update_layout(
        margin={"r":0, "t":0, "l":0, "b":0},
        coloraxis_colorbar=dict(title="Pobreza hogares (%)")
    )

    # Tablas top/bottom
    top5 = gdf.nlargest(5, col_pobreza)[[col_nom, "COD_DPTO", col_pobreza]]
    bottom5 = gdf.nsmallest(5, col_pobreza)[[col_nom, "COD_DPTO", col_pobreza]]

    return fig, top5.to_dict("records"), bottom5.to_dict("records")

# =========================
# 5. Ejecutar app
# =========================
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)

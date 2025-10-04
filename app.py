import pandas as pd
import geopandas as gpd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# ===============================
# 1️⃣ CARGA DE DATOS
# ===============================
# Archivos dentro de la carpeta "data"
geo_path = "data/departamentos.geojson"
csv_path = "data/tasas_hogares_departamento.csv"

# Leer los datos
geo = gpd.read_file(geo_path)
tasas = pd.read_csv(csv_path)

# Asegurar tipos de código iguales (2 dígitos)
geo["COD_DPTO"] = geo["COD_DPTO"].astype(str).str.zfill(2)
tasas["COD_DPTO"] = tasas["COD_DPTO"].astype(str).str.zfill(2)

# Unir GeoJSON con CSV
geo = geo.merge(tasas[["COD_DPTO", "pobreza_hog_%"]], on="COD_DPTO", how="left")

# Validar unión
print(f"Departamentos con datos: {geo['pobreza_hog_%'].notna().sum()}")
print(f"Departamentos sin datos: {geo['pobreza_hog_%'].isna().sum()}")

# ===============================
# 2️⃣ APLICACIÓN DASH
# ===============================
app = Dash(__name__)
server = app.server  # Para Render

# Layout
app.layout = html.Div([
    html.H3("Taller · Pobreza de hogares (%) — Dashboard"),
    
    html.Div([
        html.Label("Clasificación"),
        dcc.Dropdown(
            id="scheme",
            options=[
                {"label": "Quantiles", "value": "quantiles"},
                {"label": "Natural Breaks (Jenks)", "value": "natural_breaks"}
            ],
            value="quantiles",
            clearable=False,
            style={"width": "250px"}
        ),
        
        html.Label("k (clases)"),
        dcc.Slider(3, 7, 1, value=5, id="k", marks={i: str(i) for i in range(3, 8)}, tooltip={"placement": "bottom"})
    ], style={"display": "flex", "gap": "40px", "alignItems": "center"}),
    
    html.Br(),
    
    html.Div([
        html.Label("Paleta"),
        dcc.Dropdown(
            id="palette",
            options=[
                {"label": "YlOrRd", "value": "YlOrRd"},
                {"label": "BuGn", "value": "BuGn"},
                {"label": "OrRd", "value": "OrRd"},
                {"label": "Viridis", "value": "Viridis"},
                {"label": "Cividis", "value": "Cividis"},
            ],
            value="BuGn",
            clearable=False,
            style={"width": "250px"}
        )
    ]),
    
    html.Br(),
    dcc.Graph(id="mapa", style={"height": "600px"}),
])

# ===============================
# 3️⃣ CALLBACK DEL MAPA
# ===============================
@app.callback(
    Output("mapa", "figure"),
    Input("scheme", "value"),
    Input("k", "value"),
    Input("palette", "value")
)
def actualizar_mapa(scheme, k, palette):
    try:
        fig = px.choropleth_mapbox(
            geo,
            geojson=geo.__geo_interface__,
            locations="COD_DPTO",
            color="pobreza_hog_%",
            hover_name="dpto_cnmbr",
            color_continuous_scale=palette,
            mapbox_style="carto-positron",
            zoom=4,
            center={"lat": 4.5, "lon": -74.1},
            title=f"Pobreza de hogares (%) — {scheme}, k={k}",
        )
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        return fig
    except Exception as e:
        print("Error al generar el mapa:", e)
        return px.scatter(title="Error al cargar datos")

# ===============================
# 4️⃣ EJECUCIÓN LOCAL
# ===============================
if __name__ == "__main__":
    app.run_server(debug=True)

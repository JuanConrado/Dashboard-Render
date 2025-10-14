import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# ==========================
# 1. CARGA DE DATOS
# ==========================
df = pd.read_csv("data/tasas_hogares_departamento.csv")

# Asegurar tipo numérico
df["pobreza_hog_%"] = pd.to_numeric(df["pobreza_hog_%"], errors="coerce")
df["COD_DPTO"] = df["COD_DPTO"].astype(str).str.zfill(2)

# Diccionario de códigos a nombres oficiales del DANE
nombres_dptos = {
    "05": "Antioquia", "08": "Atlántico", "11": "Bogotá D.C.", "13": "Bolívar",
    "15": "Boyacá", "17": "Caldas", "18": "Caquetá", "19": "Cauca",
    "20": "Cesar", "23": "Córdoba", "25": "Cundinamarca", "27": "Chocó",
    "41": "Huila", "44": "La Guajira", "47": "Magdalena", "50": "Meta",
    "52": "Nariño", "54": "Norte de Santander", "63": "Quindío", "66": "Risaralda",
    "68": "Santander", "70": "Sucre", "73": "Tolima", "76": "Valle del Cauca",
    "81": "Arauca", "85": "Casanare", "86": "Putumayo", "88": "San Andrés",
    "91": "Amazonas", "94": "Guainía", "95": "Guaviare", "97": "Vaupés", "99": "Vichada"
}

# Agregar columna de nombres
df["DEPARTAMENTO"] = df["COD_DPTO"].map(nombres_dptos)

# -------------------------------------------------------
# Nuevo: Diccionario de coordenadas (latitud y longitud)
# de las capitales de cada departamento (valores aproximados).
# Si tienes coordenadas más precisas, reemplázalas aquí.
coords = {
    "Antioquia": (6.2518, -75.5636),
    "Atlántico": (10.9804, -74.8039),
    "Bogotá D.C.": (4.7110, -74.0721),
    "Bolívar": (10.4000, -75.5000),
    "Boyacá": (5.5353, -73.3678),
    "Caldas": (5.0703, -75.5138),
    "Caquetá": (1.6144, -75.6062),
    "Cauca": (2.4448, -76.6147),
    "Cesar": (10.4742, -73.2454),
    "Córdoba": (8.7591, -75.8786),
    "Cundinamarca": (4.7110, -74.0721),  # comparte capital con Bogotá
    "Chocó": (5.6944, -76.6611),
    "Huila": (2.9304, -75.2809),
    "La Guajira": (11.5444, -72.9072),
    "Magdalena": (11.2408, -74.1990),
    "Meta": (4.1420, -73.6266),
    "Nariño": (1.2136, -77.2811),
    "Norte de Santander": (7.8941, -72.5039),
    "Quindío": (4.5325, -75.6811),
    "Risaralda": (4.8143, -75.6946),
    "Santander": (7.1193, -73.1227),
    "Sucre": (9.3040, -75.3978),
    "Tolima": (4.4389, -75.2322),
    "Valle del Cauca": (3.4516, -76.5320),
    "Arauca": (7.0833, -70.7500),
    "Casanare": (5.3378, -72.3959),
    "Putumayo": (1.1470, -76.6472),
    "San Andrés": (12.5833, -81.7000),
    "Amazonas": (-4.2050, -69.9406),
    "Guainía": (3.8667, -67.9167),
    "Guaviare": (2.5667, -72.6460),
    "Vaupés": (1.2561, -70.2346),
    "Vichada": (6.1857, -67.4858),
}

# Crear DataFrame de coordenadas
df_coords = pd.DataFrame(
    [{"DEPARTAMENTO": dpto, "lat": lat, "lon": lon} for dpto, (lat, lon) in coords.items()]
)

# Unir con el DataFrame principal para incluir lat/lon
df = df.merge(df_coords, on="DEPARTAMENTO", how="left")

# Crear la figura del mapa (Scatter Mapbox) una sola vez.
# Representa cada departamento con un marcador cuyo tamaño y color
# dependen del porcentaje de pobreza.
fig_map = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    size="pobreza_hog_%",  # tamaño proporcional
    color="pobreza_hog_%",  # color proporcional
    color_continuous_scale="YlOrRd",
    hover_name="DEPARTAMENTO",
    size_max=30,
    zoom=4.5,
    center={"lat": 4.570868, "lon": -74.297333},
)
fig_map.update_layout(
    mapbox_style="carto-positron",
    margin={"l": 0, "r": 0, "t": 0, "b": 0},
    height=600
)

# ==========================
# 2. INICIALIZAR APP
# ==========================
app = dash.Dash(__name__)
server = app.server

# ==========================
# 3. LAYOUT
# ==========================
app.layout = html.Div([
    html.H1("📊 Dashboard: Pobreza de Hogares por Departamento — Colombia",
            style={"textAlign": "center", "color": "#0a3d62"}),

    html.Div([
        html.Div([
            html.H3("Promedio Nacional", style={"color": "#3c6382"}),
            html.H2(f"{df['pobreza_hog_%'].mean():.1f}%", style={"color": "#1e3799"})
        ], className="card"),

        html.Div([
            html.H3("Máximo", style={"color": "#3c6382"}),
            html.H2(f"{df['pobreza_hog_%'].max():.1f}%", style={"color": "#e55039"})
        ], className="card"),

        html.Div([
            html.H3("Mínimo", style={"color": "#3c6382"}),
            html.H2(f"{df['pobreza_hog_%'].min():.1f}%", style={"color": "#38ada9"})
        ], className="card"),
    ], style={"display": "flex", "justifyContent": "space-around"}),

    html.Hr(),

    html.Div([
        html.Div([
            html.Label("Selecciona Departamento 1"),
            dcc.Dropdown(
                id="depto1",
                options=[{"label": d, "value": d} for d in sorted(df["DEPARTAMENTO"].dropna().unique())],
                value="Antioquia",
                clearable=False
            ),
            html.Label("Selecciona Departamento 2"),
            dcc.Dropdown(
                id="depto2",
                options=[{"label": d, "value": d} for d in sorted(df["DEPARTAMENTO"].dropna().unique())],
                value="Chocó",
                clearable=False
            ),
        ], style={"width": "25%", "display": "inline-block", "verticalAlign": "top"}),

        html.Div([
            dcc.Graph(id="bar_chart"),
            dcc.Graph(id="hist_chart"),
        ], style={"width": "70%", "display": "inline-block", "padding": "0 2%"})
    ]),

    # Añadir la gráfica de mapa
    html.Div([
        html.H3("Mapa de pobreza por departamento", style={"textAlign": "center", "color": "#0a3d62"}),
        dcc.Graph(
            id="map_chart",
            figure=fig_map  # se utiliza la figura creada arriba
        )
    ], style={"padding": "20px"}),

    html.Div(id="comentario", style={
        "padding": "20px", "fontSize": "16px", "backgroundColor": "#f8f9fa", "borderRadius": "10px"
    })
])

# ==========================
# 4. CALLBACKS
# ==========================
@app.callback(
    [Output("bar_chart", "figure"),
     Output("hist_chart", "figure"),
     Output("comentario", "children")],
    [Input("depto1", "value"), Input("depto2", "value")]
)
def actualizar_dashboard(d1, d2):
    # --- Gráfico de barras ---
    fig_bar = px.bar(df.sort_values("pobreza_hog_%", ascending=False),
                     x="DEPARTAMENTO", y="pobreza_hog_%",
                     color="pobreza_hog_%",
                     color_continuous_scale="YlOrRd",
                     title="Pobreza por Departamento (%)")
    fig_bar.update_layout(xaxis_title=None, yaxis_title="Porcentaje", template="plotly_white")

    # --- Histograma ---
    fig_hist = px.histogram(df, x="pobreza_hog_%", nbins=10,
                            title="Distribución del índice de pobreza (%)",
                            color_discrete_sequence=["#74b9ff"])
    fig_hist.update_layout(xaxis_title="Pobreza (%)", yaxis_title="Frecuencia", template="plotly_white")

    # --- Comentario automático ---
    top = df.nlargest(2, "pobreza_hog_%")
    low = df.nsmallest(2, "pobreza_hog_%")
    prom = df["pobreza_hog_%"].mean()

    texto = f"""
    🔹 **{top.iloc[0]['DEPARTAMENTO']}** presenta el mayor nivel de pobreza (**{top.iloc[0]['pobreza_hog_%']:.1f}%**),
    seguida de **{top.iloc[1]['DEPARTAMENTO']} ({top.iloc[1]['pobreza_hog_%']:.1f}%)**.

    🔹 En contraste, los niveles más bajos se observan en **{low.iloc[0]['DEPARTAMENTO']} ({low.iloc[0]['pobreza_hog_%']:.1f}%)**
    y **{low.iloc[1]['DEPARTAMENTO']} ({low.iloc[1]['pobreza_hog_%']:.1f}%)**.

    🔹 El promedio nacional de pobreza es **{prom:.1f}%**.
    """

    if d1 and d2:
        v1 = df.loc[df["DEPARTAMENTO"] == d1, "pobreza_hog_%"].values[0]
        v2 = df.loc[df["DEPARTAMENTO"] == d2, "pobreza_hog_%"].values[0]
        diff = abs(v1 - v2)
        texto += f"\n\nComparando **{d1} ({v1:.1f}%)** con **{d2} ({v2:.1f}%)**, \
la diferencia es de **{diff:.1f} puntos porcentuales**."

    return fig_bar, fig_hist, dcc.Markdown(texto)

# ==========================
# 5. SERVIDOR
# ==========================
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050)


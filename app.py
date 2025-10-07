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

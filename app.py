import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output

# ========================================
# 1️⃣ CARGA DE DATOS
# ========================================
csv_path = "data/tasas_hogares_departamento.csv"

# ========================================
# 2️⃣ LIMPIEZA Y VALIDACIÓN
# ========================================
if not df.empty:
    if "pobreza_hog_%" in df.columns:
        df = df[["COD_DPTO", "pobreza_hog_%"]]
        df["pobreza_hog_%"] = df["pobreza_hog_%"].astype(float)
        df["NOMBRE"] = [
            "ANTIOQUIA","ATLÁNTICO","BOGOTÁ D.C.","BOLÍVAR","BOYACÁ","CALDAS",
            "CAQUETÁ","CAUCA","CÉSAR","CÓRDOBA","CUNDINAMARCA","CHOCÓ",
            "HUILA","LA GUAJIRA","MAGDALENA","META","NARIÑO","NORTE DE SANTANDER",
            "QUINDÍO","RISARALDA","SANTANDER","SUCRE","TOLIMA","VALLE DEL CAUCA"
        ][:len(df)]
        msg = f"✅ {len(df)} departamentos cargados."
    else:
        msg = "⚠️ No se encontró la columna 'pobreza_hog_%'."
else:
    msg = "⚠️ No se pudo cargar el CSV."

# ========================================
# 3️⃣ CONFIGURACIÓN DASH
# ========================================
app = Dash(__name__)
server = app.server

# ========================================
# 4️⃣ LAYOUT
# ========================================
app.layout = html.Div([
    html.H2("Dashboard Interactivo — Pobreza de Hogares (%) en Colombia"),
    html.P(status),
    html.P(msg),

    html.Div([
        html.Div([
            html.H4("📊 Promedio:"),
            html.H3(f"{df['pobreza_hog_%'].mean():.2f}%")
        ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),

        html.Div([
            html.H4("📈 Mediana:"),
            html.H3(f"{df['pobreza_hog_%'].median():.2f}%")
        ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),

        html.Div([
            html.H4("🚨 Máximo:"),
            html.H3(f"{df['pobreza_hog_%'].max():.2f}%")
        ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),
    ], style={'marginBottom': '30px'}),

    html.Hr(),

    html.Div([
        html.Label("Seleccionar departamento:"),
        dcc.Dropdown(
            id="departamento",
            options=[{"label": i, "value": i} for i in df["NOMBRE"]],
            value=df["NOMBRE"][0],
            style={'width': '50%'}
        )
    ]),

    html.Br(),

    html.Div([
        dcc.Graph(id="grafico_top"),
        dcc.Graph(id="grafico_hist"),
        dcc.Graph(id="grafico_linea")
    ]),

    html.Hr(),
    html.H4("Tabla completa de datos:"),
    dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "5px"},
        page_size=10
    )
])

# ========================================
# 5️⃣ CALLBACKS
# ========================================

@app.callback(
    Output("grafico_top", "figure"),
    Output("grafico_hist", "figure"),
    Output("grafico_linea", "figure"),
    Input("departamento", "value")
)
def actualizar_graficos(depto_sel):
    # TOP 10
    df_sorted = df.sort_values("pobreza_hog_%", ascending=False).head(10)
    fig_top = px.bar(
        df_sorted,
        x="NOMBRE",
        y="pobreza_hog_%",
        text="pobreza_hog_%",
        color="pobreza_hog_%",
        color_continuous_scale="YlOrRd",
        title="Top 10 Departamentos con mayor pobreza (%)"
    )
    fig_top.update_traces(texttemplate='%{text:.2f}%', textposition='outside')

    # HISTOGRAMA
    fig_hist = px.histogram(
        df,
        x="pobreza_hog_%",
        nbins=10,
        color_discrete_sequence=["#3182bd"],
        title="Distribución general de pobreza (%)"
    )

    # LÍNEA ordenada
    fig_line = px.line(
        df.sort_values("pobreza_hog_%"),
        x="NOMBRE",
        y="pobreza_hog_%",
        title=f"Tendencia de pobreza por departamento (seleccionado: {depto_sel})",
        markers=True
    )

    # Resalta el departamento seleccionado
    sel = df[df["NOMBRE"] == depto_sel]
    if not sel.empty:
        fig_line.add_scatter(
            x=sel["NOMBRE"], y=sel["pobreza_hog_%"],
            mode="markers+text", marker=dict(color="red", size=12),
            text=[f"{sel['pobreza_hog_%'].values[0]:.1f}%"], name="Seleccionado"
        )

    return fig_top, fig_hist, fig_line

# ========================================
# 6️⃣ MAIN
# ========================================
if __name__ == "__main__":
    app.run_server(debug=True)

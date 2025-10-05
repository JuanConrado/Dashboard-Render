import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output

# ========================================
# 1️⃣ CARGA DE DATOS
# ========================================
csv_path = "data/tasas_hogares_departamento.csv"

try:
    df = pd.read_csv(csv_path)
    df["COD_DPTO"] = df["COD_DPTO"].astype(str).str.zfill(2)
    status = "✅ Archivo CSV cargado correctamente."
except Exception as e:
    df = pd.DataFrame()
    status = f"❌ Error al cargar CSV: {e}"

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
# 3️⃣ APLICACIÓN DASH
# ========================================
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Dashboard — Pobreza de Hogares (%) en Colombia"),
    html.P(status),
    html.P(msg),

    html.Hr(),
    html.H4("Exploración interactiva"),
    
    html.Label("Número de barras a mostrar:"),
    dcc.Slider(5, 24, 1, value=10, id="slider_n"),

    dcc.Graph(id="bar_chart"),

    html.Hr(),
    html.H4("Tabla resumen de pobreza:"),
    dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        style_table={"overflowX": "auto", "maxWidth": "800px"},
        style_cell={"textAlign": "left", "padding": "5px"},
        page_size=10
    )
])

# ========================================
# 4️⃣ CALLBACK
# ========================================
@app.callback(
    Output("bar_chart", "figure"),
    Input("slider_n", "value")
)
def update_chart(n):
    if df.empty:
        return px.bar(title="No hay datos disponibles.")
    
    df_sorted = df.sort_values("pobreza_hog_%", ascending=False).head(n)
    fig = px.bar(
        df_sorted,
        x="NOMBRE",
        y="pobreza_hog_%",
        text="pobreza_hog_%",
        color="pobreza_hog_%",
        color_continuous_scale="YlOrRd",
        title=f"Top {n} Departamentos con mayor pobreza (%)"
    )
    fig.update_layout(xaxis_title="Departamento", yaxis_title="Pobreza (%)")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)

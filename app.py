import pandas as pd
import geopandas as gpd
from dash import Dash, html, dcc, dash_table

# ===============================
# 1️⃣ CARGA DE DATOS
# ===============================
geo_path = "data/departamentos.geojson"
csv_path = "data/tasas_hogares_departamento.csv"

try:
    geo = gpd.read_file(geo_path)
    tasas = pd.read_csv(csv_path)
    status = "✅ Archivos cargados correctamente."
except Exception as e:
    geo, tasas = None, None
    status = f"❌ Error al cargar archivos: {e}"

# ===============================
# 2️⃣ PREPARACIÓN DE DATOS
# ===============================
if geo is not None and tasas is not None:
    try:
        geo["COD_DPTO"] = geo["COD_DPTO"].astype(str).str.zfill(2)
        tasas["COD_DPTO"] = tasas["COD_DPTO"].astype(str).str.zfill(2)

        merged = geo.merge(
            tasas[["COD_DPTO", "pobreza_hog_%"]],
            on="COD_DPTO",
            how="left"
        )

        msg = f"✅ Unión exitosa. Departamentos con datos: {merged['pobreza_hog_%'].notna().sum()}"
        tabla = merged[["COD_DPTO", "dpto_cnmbr", "pobreza_hog_%"]].head(10)
    except Exception as e:
        merged, msg, tabla = None, f"❌ Error al unir datos: {e}", pd.DataFrame()
else:
    msg, tabla = "⚠️ No se cargaron los datos.", pd.DataFrame()

# ===============================
# 3️⃣ APLICACIÓN DASH
# ===============================
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Diagnóstico — Georreferenciación Taller 2"),
    html.P(status),
    html.P(msg),

    html.Hr(),
    html.H4("Vista previa de los datos unificados:"),
    
    dash_table.DataTable(
        data=tabla.to_dict("records"),
        columns=[{"name": c, "id": c} for c in tabla.columns],
        style_table={"overflowX": "auto", "maxWidth": "800px"},
        style_cell={"textAlign": "left", "padding": "5px"},
        page_size=10
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)

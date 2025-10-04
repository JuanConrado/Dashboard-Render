import json, pathlib
import numpy as np
import pandas as pd
import mapclassify as mc
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, dash_table

# Rutas
DATA_DIR = pathlib.Path(__file__).parent / "data"
PATH_GEOJSON = DATA_DIR / "departamentos.geojson"
PATH_TASAS   = DATA_DIR / "tasas_hogares_departamento.csv"

# Carga
with open(PATH_GEOJSON, "r", encoding="utf-8") as f:
    GEOJSON = json.load(f)

df = pd.read_csv(PATH_TASAS, dtype={"COD_DPTO": str})

# Nombre de etiqueta (buscar la que exista)
props = {feat["properties"]["COD_DPTO"]: feat["properties"] for feat in GEOJSON["features"]}
name_keys = ["DPTO_CNMBR","DPTO_CNMBRE","dpto_cnmbr","dpto_cnmbre"]
def get_name(code):
    d = props.get(code, {})
    for k in name_keys:
        if k in d and pd.notna(d[k]): return d[k]
    return code

df["NOMBRE"] = df["COD_DPTO"].apply(get_name)

VAL_COL = "pobreza_hog_%"
assert VAL_COL in df.columns, f"No encuentro {VAL_COL} en el CSV."

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Taller · Pobreza de hogares (%) — Dashboard"),
    html.Div([
        html.Div([
            html.Label("Clasificación"),
            dcc.Dropdown(id="scheme",
                options=[{"label":"Quantiles","value":"quantiles"},
                         {"label":"Jenks (Natural Breaks)","value":"jenks"}],
                value="quantiles", clearable=False)
        ], style={"width":"32%","display":"inline-block","marginRight":"1%"}),
        html.Div([
            html.Label("k (clases)"),
            dcc.Slider(id="k", min=3, max=7, step=1, value=5,
                       marks={i:str(i) for i in range(3,8)})
        ], style={"width":"32%","display":"inline-block","marginRight":"1%"}),
        html.Div([
            html.Label("Paleta"),
            dcc.Dropdown(id="palette",
                options=[{"label":c,"value":c} for c in ["YlOrRd","BuGn","PuRd","Oranges","Greens","Blues"]],
                value="YlOrRd", clearable=False)
        ], style={"width":"32%","display":"inline-block"})
    ], style={"marginBottom":"10px"}),

    dcc.Graph(id="mapa", style={"height":"70vh"}),

    html.Div([
        html.Div([
            html.H4("Top 5 (%)"),
            dash_table.DataTable(id="top5",
                columns=[{"name":c,"id":c} for c in ["NOMBRE","COD_DPTO",VAL_COL]],
                page_size=5, style_table={"overflowX":"auto"})
        ], style={"width":"49%","display":"inline-block"}),
        html.Div([
            html.H4("Bottom 5 (%)"),
            dash_table.DataTable(id="bot5",
                columns=[{"name":c,"id":c} for c in ["NOMBRE","COD_DPTO",VAL_COL]],
                page_size=5, style_table={"overflowX":"auto"})
        ], style={"width":"49%","display":"inline-block","float":"right"})
    ])
], style={"maxWidth":"1200px","margin":"0 auto","padding":"10px"})

def compute_bins(values, scheme="quantiles", k=5):
    vals = pd.Series(values).dropna()
    if len(vals) == 0: return None
    ci = mc.NaturalBreaks(vals, k=k) if scheme=="jenks" else mc.Quantiles(vals, k=k)
    brks = np.asarray(ci.bins, dtype=float)
    # cubrir extremos para evitar “outside color scale”
    brks[0]  = min(vals.min(), brks[0]) - 1e-9
    brks[-1] = max(vals.max(), brks[-1]) + 1e-9
    return brks

@app.callback(
    Output("mapa","figure"),
    Output("top5","data"),
    Output("bot5","data"),
    Input("scheme","value"),
    Input("k","value"),
    Input("palette","value"),
)
def update_map(scheme, k, palette):
    bins = compute_bins(df[VAL_COL], scheme=scheme, k=int(k))
    fig = px.choropleth(
        df, geojson=GEOJSON, color=VAL_COL, locations="COD_DPTO",
        featureidkey="properties.COD_DPTO",
        hover_name="NOMBRE",
        color_continuous_scale=palette,
        range_color=(df[VAL_COL].min(), df[VAL_COL].max())
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=0,r=0,t=10,b=0),
                      coloraxis_colorbar=dict(title="Pobreza hogares (%)"))

    # Top/bottom 5
    t5 = df.sort_values(VAL_COL, ascending=False)[["NOMBRE","COD_DPTO",VAL_COL]].head(5).round({VAL_COL:1})
    b5 = df.sort_values(VAL_COL, ascending=True)[["NOMBRE","COD_DPTO",VAL_COL]].head(5).round({VAL_COL:1})
    return fig, t5.to_dict("records"), b5.to_dict("records")

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)

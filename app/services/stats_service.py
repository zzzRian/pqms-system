import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.io import to_html

def compute_measures(values):
    if not values:
        return {}
    s = pd.Series(values, dtype=float)
    mode = s.mode()
    return {
        "n": int(s.count()),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "mode": float(mode.iloc[0]) if not mode.empty else None,
        "range": float(s.max() - s.min()),
        "variance": float(s.var(ddof=0)),
        "std": float(s.std(ddof=0)),
        "min": float(s.min()),
        "max": float(s.max()),
    }

def frequency_table(values, bins=None):
    if not values:
        return []
    s = pd.Series(values, dtype=float)
    n = len(s)
    if n < 20:
        counts = s.value_counts().sort_index()
        fac = counts.cumsum()
        rel = counts / n
        rows = []
        for value, count, acc, r in zip(counts.index, counts.values, fac.values, rel.values):
            rows.append({
                "intervalo": f"{value:.3f}",
                "fa": int(count),
                "fac": int(acc),
                "fr": round(float(r), 4),
                "pct": round(float(r * 100), 2),
            })
        return rows

    if bins is None:
        bins = max(5, int(round(1 + 3.322 * math.log10(n)))) if n > 1 else 1
    cut = pd.cut(s, bins=bins, include_lowest=True)
    fa = cut.value_counts().sort_index()
    fac = fa.cumsum()
    rel = fa / n
    rows = []
    for interval, count, acc, r in zip(fa.index, fa.values, fac.values, rel.values):
        rows.append({
            "intervalo": f"[{interval.left:.3f}, {interval.right:.3f}]",
            "fa": int(count),
            "fac": int(acc),
            "fr": round(float(r), 4),
            "pct": round(float(r * 100), 2),
        })
    return rows

def deviation_table(values):
    s = pd.Series(values, dtype=float)
    mean = s.mean()
    rows = []
    for v in s:
        dev = v - mean
        rows.append({
            "xi": round(float(v), 3),
            "dev": round(float(dev), 4),
            "dev2": round(float(dev ** 2), 4),
        })
    return rows, float(mean)

def histogram_html(values, labels=None, title="Histograma"):
    if not values:
        return "<p class='text-muted'>Sin datos</p>"
    if labels is None or len(labels) != len(values):
        labels = [f"Lote {i}" for i in range(1, len(values) + 1)]
    df = pd.DataFrame({"Lote": labels, "% Alcohol": values})
    fig = px.bar(df, x="Lote", y="% Alcohol", color="Lote", title=title,
                 labels={"Lote": "Lote", "% Alcohol": "% Alcohol"},
                 color_discrete_sequence=px.colors.qualitative.Prism)
    fig.update_traces(hovertemplate="<b>Lote: %{x}</b><br>% Alcohol: %{y:.3f}<extra></extra>")
    fig.update_layout(template="plotly_white", height=380,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                      xaxis_tickangle=-45,
                      margin=dict(t=80, b=120, l=60, r=60))
    return to_html(fig, full_html=False, include_plotlyjs="cdn")

def control_chart_html(values, title="Gráfica de Control X-individual"):
    if not values:
        return "<p class='text-muted'>Sin datos</p>"
    s = pd.Series(values, dtype=float)
    mean = s.mean()
    std = s.std(ddof=0)
    ucl = mean + 3 * std
    lcl = mean - 3 * std
    x = [f"Obs {i}" for i in range(1, len(s) + 1)]
    colors = px.colors.qualitative.Dark24
    marker_colors = [colors[i % len(colors)] for i in range(len(s))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=s, mode="lines+markers", name="% Alcohol por muestra",
        line=dict(color="#7b2cbf", width=2),
        marker=dict(size=10, color=marker_colors),
        hovertemplate="<b>%{x}</b><br>% Alcohol: %{y:.3f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=[ucl] * len(s), mode="lines", name=f"LCS = {ucl:.2f}",
        line=dict(color="#e63946", width=1.5, dash="dash"), hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=x, y=[mean] * len(s), mode="lines", name=f"LC (x̄) = {mean:.2f}",
        line=dict(color="#2a9d8f", width=1.5, dash="dash"), hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=x, y=[lcl] * len(s), mode="lines", name=f"LCI = {lcl:.2f}",
        line=dict(color="#e63946", width=1.5, dash="dash"), hoverinfo="skip"
    ))
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(title="Observación", tickmode="array", tickvals=x, ticktext=x,
                   showgrid=False, showline=True, linecolor="#cccccc"),
        yaxis=dict(title="% Alcohol", tickmode="linear", tick0=0, dtick=1,
                   gridcolor="#f0f0f0", showline=False),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#4a4a4a", font_size=12, font_color="white"),
        margin=dict(t=80, b=120, l=60, r=60)
    )
    return to_html(fig, full_html=False, include_plotlyjs="cdn"), {
        "mean": mean, "ucl": ucl, "lcl": lcl, "std": std
    }

def pareto_html(values, title="Diagrama de Pareto"):
    if not values:
        return "<p class='text-muted'>Sin datos</p>"
    s = pd.Series(values, dtype=float).round(3)
    counts = s.value_counts().reset_index()
    counts.columns = ["alcohol", "count"]
    counts = counts.sort_values(["count", "alcohol"], ascending=[False, False])
    counts["cum_pct"] = counts["count"].cumsum() / counts["count"].sum() * 100
    colors = px.colors.qualitative.Set3
    bar_colors = [colors[i % len(colors)] for i in range(len(counts))]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=counts["alcohol"].astype(str), y=counts["count"], name="Frecuencia absoluta",
        marker_color=bar_colors,
        hovertemplate="<b>% Alcohol: %{x}</b><br>Frecuencia: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=counts["alcohol"].astype(str), y=counts["cum_pct"], name="Hi% acumulada",
        yaxis="y2", mode="lines+markers", line=dict(color="#1f2937", width=2),
        marker=dict(size=8, color="#1f2937"),
        customdata=counts[["cum_pct"]],
        hovertemplate="<b>% Alcohol: %{x}</b><br>Frecuencia: %{y}<br>Hi% acumulada: %{customdata[0]:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        yaxis=dict(title="Frecuencia absoluta"),
        yaxis2=dict(title="Hi% acumulada", overlaying="y", side="right", range=[0, 100], showgrid=False),
        hovermode="x unified",
        margin=dict(t=90, b=120, l=60, r=60)
    )
    return to_html(fig, full_html=False, include_plotlyjs="cdn")

def ishikawa_html(problem, causes):
    """Simple Ishikawa rendering with plotly."""
    fig = go.Figure()
    categories = ["Mano de obra", "Métodos", "Materiales", "Maquinaria", "Medición", "Medio ambiente"]
    y_positions = [3, 3, 2, 1, 1, 2]
    x_positions = [1, 3, 1, 1, 3, 3]
    for cat, x, y in zip(categories, x_positions, y_positions):
        fig.add_annotation(x=x, y=y + 0.4, text=f"<b>{cat}</b>", showarrow=False)
        sub = causes.get(cat, [])
        for i, c in enumerate(sub[:3]):
            fig.add_annotation(x=x + 0.1, y=y + 0.2 - i * 0.15, text=f"• {c}", showarrow=False,
                               xanchor="left", font=dict(size=10))
    fig.add_annotation(x=5, y=2, text=f"<b>{problem}</b>", showarrow=False,
                       bgcolor="#c47b1d", font=dict(color="white", size=12))
    fig.update_xaxes(visible=False, range=[0, 6])
    fig.update_yaxes(visible=False, range=[0, 4])
    fig.update_layout(template="plotly_white", height=360, title="Diagrama de Ishikawa")
    return to_html(fig, full_html=False, include_plotlyjs="cdn")

from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import extract
from app.models import Batch
from app.services.stats_service import (
    compute_measures, frequency_table, deviation_table,
    histogram_html, control_chart_html, pareto_html, ishikawa_html
)

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/")
@login_required
def dashboard():
    beer_filter = request.args.get("beer_type", "")
    month_filter = request.args.get("month", "")
    q = Batch.query
    if beer_filter:
        q = q.filter_by(beer_type=beer_filter)
    if month_filter.isdigit():
        q = q.filter(extract("month", Batch.date) == int(month_filter))
    batches = q.order_by(Batch.date.asc()).all()
    values = [b.alcohol_pct for b in batches]

    measures = compute_measures(values)
    freq = frequency_table(values)
    dev, mean = deviation_table(values) if values else ([], 0)
    codes = [b.code for b in batches]
    hist = histogram_html(values, codes, "Histograma del % de Alcohol")
    ctrl_result = control_chart_html(values) if values else ("<p class='text-muted'>Sin datos</p>", {})
    ctrl_html, ctrl_meta = ctrl_result if isinstance(ctrl_result, tuple) else (ctrl_result, {})

    pareto = pareto_html(values, "Pareto del % de Alcohol por lote")

    comparison = []
    types = sorted({b.beer_type for b in batches})
    for t in types:
        vs = [b.alcohol_pct for b in batches if b.beer_type == t]
        m = compute_measures(vs)
        comparison.append({"type": t, "n": m.get("n", 0),
                           "mean": m.get("mean", 0), "std": m.get("std", 0)})

    alerts = []
    if ctrl_meta:
        for b in batches:
            if b.alcohol_pct > ctrl_meta["ucl"] or b.alcohol_pct < ctrl_meta["lcl"]:
                alerts.append(f"⚠️ Lote {b.code} fuera de control estadístico ({b.alcohol_pct}%)")

    ishikawa = ishikawa_html("Alcohol fuera de rango", {
        "Mano de obra": ["Falta capacitación", "Error humano"],
        "Métodos": ["Procedimiento no actualizado"],
        "Materiales": ["Lúpulo variable", "Malta húmeda"],
        "Maquinaria": ["Fermentador descalibrado"],
        "Medición": ["Densímetro impreciso"],
        "Medio ambiente": ["Temperatura inestable"],
    })

    month_numbers = sorted({b.date.month for b in Batch.query.order_by(Batch.date.asc()).all()})
    spanish_month_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                           "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    month_options = [
        {"value": m, "label": spanish_month_names[m - 1]}
        for m in month_numbers
    ]

    return render_template("stats/dashboard.html",
                           measures=measures, freq=freq, dev=dev, mean=mean,
                           hist=hist, ctrl=ctrl_html, pareto=pareto, ishikawa=ishikawa,
                           comparison=comparison, alerts=alerts,
                           beer_filter=beer_filter,
                           beer_types=sorted({b.beer_type for b in Batch.query.all()}),
                           month_filter=month_filter,
                           month_options=month_options)

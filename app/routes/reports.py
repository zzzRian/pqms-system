import io
import pandas as pd
from flask import Blueprint, render_template, send_file
from flask_login import login_required
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from app.models import Batch, Claim, NonConformity, Audit
from app.services.stats_service import compute_measures

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/")
@login_required
def index():
    return render_template("reports/index.html")

@reports_bp.route("/excel/production")
@login_required
def excel_production():
    batches = Batch.query.all()
    df = pd.DataFrame([{
        "Código": b.code, "Fecha": b.date, "Tipo": b.beer_type,
        "Operario": b.operator.full_name if b.operator else "",
        "% Alcohol": b.alcohol_pct, "Estado": b.status
    } for b in batches])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Producción")
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="produccion.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@reports_bp.route("/pdf/statistics")
@login_required
def pdf_statistics():
    batches = Batch.query.all()
    m = compute_measures([b.alcohol_pct for b in batches])
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    c.setFillColorRGB(0.77, 0.48, 0.11)
    c.rect(0, h - 60, w, 60, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, h - 40, "PERUVIAM - Reporte Estadístico de Calidad")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 11)
    y = h - 100
    c.drawString(40, y, f"Total de lotes: {len(batches)}")
    for k, v in m.items():
        y -= 18
        c.drawString(40, y, f"{k.capitalize()}: {round(v, 4) if isinstance(v, float) else v}")
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Últimos lotes:")
    c.setFont("Helvetica", 10)
    for b in batches[-15:]:
        y -= 14
        if y < 60: c.showPage(); y = h - 60
        c.drawString(40, y, f"{b.code} | {b.beer_type} | {b.alcohol_pct}% | {b.status}")
    c.save()
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="reporte_estadistico.pdf",
                     mimetype="application/pdf")

@reports_bp.route("/pdf/iso")
@login_required
def pdf_iso():
    ncs = NonConformity.query.all()
    audits = Audit.query.all()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    c.setFillColorRGB(0.77, 0.48, 0.11); c.rect(0, h-60, w, 60, fill=1, stroke=0)
    c.setFillColorRGB(1,1,1); c.setFont("Helvetica-Bold", 18)
    c.drawString(40, h-40, "PERUVIAM - Reporte ISO 9000")
    c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 12)
    y = h - 90
    c.drawString(40, y, "Auditorías:"); c.setFont("Helvetica", 10)
    for a in audits:
        y -= 14
        if y < 80: c.showPage(); y = h - 60
        c.drawString(40, y, f"{a.date} - {a.title} ({a.status})")
    y -= 24; c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "No conformidades:")
    c.setFont("Helvetica", 10)
    for nc in ncs:
        y -= 14
        if y < 80: c.showPage(); y = h - 60
        c.drawString(40, y, f"#{nc.id} {nc.description[:80]} → {nc.status}")
    c.save(); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="reporte_iso.pdf", mimetype="application/pdf")

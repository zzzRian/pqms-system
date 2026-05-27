from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import Batch, Claim, User
from app.services.stats_service import compute_measures

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@login_required
def home():
    beer = request.args.get("beer_type", "")
    status = request.args.get("status", "")
    operator = request.args.get("operator", "")

    q = Batch.query
    if beer: q = q.filter_by(beer_type=beer)
    if status: q = q.filter_by(status=status)
    if operator: q = q.filter_by(operator_id=int(operator))
    batches = q.all()

    total = len(batches)
    rejected = sum(1 for b in batches if b.status == "Rechazado")
    approved = sum(1 for b in batches if b.status == "Aprobado")
    in_process = sum(1 for b in batches if b.status == "En proceso")
    pct_defective = (rejected / total * 100) if total else 0
    compliance = (approved / total * 100) if total else 0
    claims_count = Claim.query.count()
    measures = compute_measures([b.alcohol_pct for b in batches])

    kpis = {
        "total": total,
        "rejected": rejected,
        "approved": approved,
        "in_process": in_process,
        "pct_defective": round(pct_defective, 2),
        "compliance": round(compliance, 2),
        "avg_alcohol": round(measures.get("mean", 0), 2),
        "variability": round(measures.get("std", 0), 3),
        "claims": claims_count,
        "cost_quality": round(rejected * 850.0, 2),
    }

    operators = User.query.filter_by(role="operario").all()
    types = sorted({b.beer_type for b in Batch.query.all()})
    return render_template("dashboard/home.html", kpis=kpis, batches=batches[:10],
                           operators=operators, types=types,
                           beer=beer, status=status, operator=operator)

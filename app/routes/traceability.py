from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import Batch

traceability_bp = Blueprint("traceability", __name__)

@traceability_bp.route("/")
@login_required
def index():
    code = request.args.get("code", "").strip()
    batch = None
    if code:
        batch = Batch.query.filter_by(code=code).first()
    batches = Batch.query.order_by(Batch.created_at.desc()).limit(30).all()
    return render_template("traceability/index.html", batch=batch, batches=batches, code=code)

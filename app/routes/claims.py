from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Claim, Batch, CLAIM_STATUS
from app.middlewares import role_required

claims_bp = Blueprint("claims", __name__)

@claims_bp.route("/")
@login_required
def index():
    claims = Claim.query.order_by(Claim.created_at.desc()).all()
    batches = Batch.query.order_by(Batch.code).all()
    return render_template("claims/index.html", claims=claims, batches=batches, statuses=CLAIM_STATUS)

@claims_bp.route("/new", methods=["POST"])
@login_required
def new():
    c = Claim(batch_id=int(request.form["batch_id"]),
              customer=request.form["customer"],
              description=request.form["description"])
    db.session.add(c)
    db.session.commit()
    flash("Reclamo registrado", "success")
    return redirect(url_for("claims.index"))

@claims_bp.route("/<int:cid>/status", methods=["POST"])
@login_required
@role_required("admin", "supervisor")
def update_status(cid):
    c = Claim.query.get_or_404(cid)
    c.status = request.form["status"]
    db.session.commit()
    flash("Estado del reclamo actualizado", "success")
    return redirect(url_for("claims.index"))

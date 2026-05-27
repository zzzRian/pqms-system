import os, uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Batch, Evidence, LOT_STATUS
from app.middlewares import role_required
from app.services.audit_service import log_action
from app.services.stats_service import compute_measures, frequency_table, deviation_table

production_bp = Blueprint("production", __name__)

BEER_TYPES = ["IPA", "Lager", "Stout", "Pilsner", "Porter", "Ale", "Wheat"]

@production_bp.route("/")
@login_required
def list_batches():
    if current_user.role == "operario":
        batches = Batch.query.filter_by(operator_id=current_user.id).order_by(Batch.created_at.desc()).all()
    else:
        batches = Batch.query.order_by(Batch.created_at.desc()).all()
    values = [b.alcohol_pct for b in batches]
    measures = compute_measures(values)
    freq = frequency_table(values)
    dev, mean = deviation_table(values) if values else ([], 0)
    return render_template("production/list.html",
                           batches=batches, statuses=LOT_STATUS, beer_types=BEER_TYPES,
                           measures=measures, freq=freq, dev=dev, mean=mean)

@production_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin", "operario", "supervisor")
def new_batch():
    if request.method == "POST":
        code = request.form["code"].strip()
        if Batch.query.filter_by(code=code).first():
            flash("Código de lote ya existe", "danger")
            return redirect(url_for("production.new_batch"))
        b = Batch(
            code=code,
            date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
            beer_type=request.form["beer_type"],
            operator_id=current_user.id,
            alcohol_pct=float(request.form["alcohol_pct"]),
            status=request.form.get("status", "En proceso"),
            notes=request.form.get("notes", ""),
        )
        db.session.add(b)
        db.session.commit()

        files = request.files.getlist("evidences")
        for f in files:
            if f and f.filename:
                fname = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
                f.save(os.path.join(current_app.config["UPLOAD_FOLDER"], fname))
                db.session.add(Evidence(batch_id=b.id, filename=fname, original_name=f.filename))
        db.session.commit()
        log_action(current_user, f"Registró lote {b.code}")
        flash("Lote registrado correctamente", "success")
        return redirect(url_for("production.list_batches"))
    return render_template("production/form.html",
                           statuses=LOT_STATUS, beer_types=BEER_TYPES,
                           today=datetime.utcnow().date().isoformat())

@production_bp.route("/<int:batch_id>")
@login_required
def detail(batch_id):
    b = Batch.query.get_or_404(batch_id)
    return render_template("production/detail.html", b=b)

@production_bp.route("/<int:batch_id>/status", methods=["POST"])
@login_required
@role_required("admin", "supervisor")
def change_status(batch_id):
    b = Batch.query.get_or_404(batch_id)
    b.status = request.form["status"]
    db.session.commit()
    log_action(current_user, f"Cambió estado lote {b.code} → {b.status}")
    flash("Estado actualizado", "success")
    return redirect(url_for("production.detail", batch_id=b.id))

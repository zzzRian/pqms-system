import os, uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import IsoDocument, Audit, NonConformity
from app.middlewares import role_required
from app.services.audit_service import log_action

iso_bp = Blueprint("iso", __name__)

@iso_bp.route("/")
@login_required
def index():
    docs = IsoDocument.query.order_by(IsoDocument.created_at.desc()).all()
    audits = Audit.query.order_by(Audit.date.desc()).all()
    ncs = NonConformity.query.order_by(NonConformity.created_at.desc()).all()
    return render_template("iso/index.html", docs=docs, audits=audits, ncs=ncs)

@iso_bp.route("/docs/new", methods=["POST"])
@login_required
@role_required("admin", "supervisor")
def new_doc():
    f = request.files.get("file")
    fname = None
    if f and f.filename:
        fname = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
        f.save(os.path.join(current_app.config["UPLOAD_FOLDER"], fname))
    d = IsoDocument(title=request.form["title"],
                    category=request.form.get("category"),
                    description=request.form.get("description"),
                    filename=fname)
    db.session.add(d)
    db.session.commit()
    log_action(current_user, f"Subió documento ISO: {d.title}")
    flash("Documento agregado", "success")
    return redirect(url_for("iso.index"))

@iso_bp.route("/audits/new", methods=["POST"])
@login_required
@role_required("admin", "supervisor")
def new_audit():
    from datetime import datetime
    a = Audit(title=request.form["title"],
              auditor=request.form.get("auditor"),
              findings=request.form.get("findings"),
              date=datetime.strptime(request.form["date"], "%Y-%m-%d").date() if request.form.get("date") else datetime.utcnow().date())
    db.session.add(a)
    db.session.commit()
    log_action(current_user, f"Registró auditoría: {a.title}")
    flash("Auditoría registrada", "success")
    return redirect(url_for("iso.index"))

@iso_bp.route("/nc/new", methods=["POST"])
@login_required
@role_required("admin", "supervisor")
def new_nc():
    nc = NonConformity(description=request.form["description"],
                       corrective_action=request.form.get("corrective_action"))
    db.session.add(nc)
    db.session.commit()
    log_action(current_user, "Registró no conformidad")
    flash("No conformidad registrada", "success")
    return redirect(url_for("iso.index"))

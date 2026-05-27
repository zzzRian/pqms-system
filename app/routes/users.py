from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, AuditLog, ROLES
from app.middlewares import role_required
from app.services.audit_service import log_action

users_bp = Blueprint("users", __name__)

@users_bp.route("/")
@login_required
@role_required("admin")
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(30).all()
    return render_template("users/list.html", users=users, logs=logs, roles=ROLES)

@users_bp.route("/create", methods=["POST"])
@login_required
@role_required("admin")
def create_user():
    u = User(
        username=request.form["username"].strip(),
        email=request.form["email"].strip(),
        full_name=request.form["full_name"].strip(),
        role=request.form["role"],
        active=True,
    )
    u.set_password(request.form["password"])
    db.session.add(u)
    db.session.commit()
    log_action(current_user, f"Creó usuario {u.username}")
    flash("Usuario creado", "success")
    return redirect(url_for("users.list_users"))

@users_bp.route("/<int:user_id>/edit", methods=["POST"])
@login_required
@role_required("admin")
def edit_user(user_id):
    u = User.query.get_or_404(user_id)
    u.full_name = request.form["full_name"].strip()
    u.email = request.form["email"].strip()
    u.role = request.form["role"]
    u.active = request.form.get("active") == "on"
    pw = request.form.get("password")
    if pw:
        u.set_password(pw)
    db.session.commit()
    log_action(current_user, f"Editó usuario {u.username}")
    flash("Usuario actualizado", "success")
    return redirect(url_for("users.list_users"))

@users_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_user(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash("No puede eliminar su propio usuario", "warning")
        return redirect(url_for("users.list_users"))
    db.session.delete(u)
    db.session.commit()
    log_action(current_user, f"Eliminó usuario {u.username}")
    flash("Usuario eliminado", "info")
    return redirect(url_for("users.list_users"))

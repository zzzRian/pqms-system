from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.services.audit_service import log_action

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.active and user.check_password(password):
            login_user(user)
            log_action(user, "Inicio de sesión")
            flash(f"Bienvenido, {user.full_name}", "success")
            return redirect(url_for("dashboard.home"))
        flash("Credenciales inválidas", "danger")
    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    log_action(current_user, "Cierre de sesión")
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("auth.login"))

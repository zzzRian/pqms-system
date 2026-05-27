from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Course, Enrollment, User
from app.middlewares import role_required

training_bp = Blueprint("training", __name__)

@training_bp.route("/")
@login_required
def index():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    if current_user.role == "admin":
        enrollments = Enrollment.query.all()
    else:
        enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    return render_template("training/index.html", courses=courses, enrollments=enrollments)

@training_bp.route("/courses/new", methods=["POST"])
@login_required
@role_required("admin")
def new_course():
    c = Course(title=request.form["title"], topic=request.form.get("topic"),
               description=request.form.get("description"),
               resource_url=request.form.get("resource_url"))
    db.session.add(c)
    db.session.commit()
    flash("Curso creado", "success")
    return redirect(url_for("training.index"))

@training_bp.route("/enroll/<int:course_id>", methods=["POST"])
@login_required
def enroll(course_id):
    e = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if not e:
        e = Enrollment(user_id=current_user.id, course_id=course_id, status="En progreso")
        db.session.add(e)
        db.session.commit()
        flash("Inscripción exitosa", "success")
    return redirect(url_for("training.index"))

@training_bp.route("/complete/<int:enrollment_id>", methods=["POST"])
@login_required
def complete(enrollment_id):
    e = Enrollment.query.get_or_404(enrollment_id)
    if e.user_id != current_user.id and current_user.role != "admin":
        flash("No autorizado", "danger")
        return redirect(url_for("training.index"))
    e.status = "Completado"
    e.score = float(request.form.get("score", 100))
    e.completed_at = datetime.utcnow()
    db.session.commit()
    flash("Curso completado", "success")
    return redirect(url_for("training.index"))

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

ROLES = ("admin", "supervisor", "operario")
LOT_STATUS = ("En proceso", "Aprobado", "Rechazado")
CLAIM_STATUS = ("Abierto", "En revisión", "Resuelto", "Cerrado")

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="operario")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *roles):
        return self.role in roles


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(255), nullable=False)
    detail = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User")


class Batch(db.Model):
    __tablename__ = "batches"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    beer_type = db.Column(db.String(60), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    alcohol_pct = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="En proceso")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    operator = db.relationship("User")
    evidences = db.relationship("Evidence", backref="batch", cascade="all, delete-orphan")
    claims = db.relationship("Claim", backref="batch", cascade="all, delete-orphan")


class Evidence(db.Model):
    __tablename__ = "evidences"
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"))
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class IsoDocument(db.Model):
    __tablename__ = "iso_documents"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80))  # Procedimiento / Manual / Norma
    description = db.Column(db.Text)
    filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Audit(db.Model):
    __tablename__ = "audits"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    auditor = db.Column(db.String(120))
    findings = db.Column(db.Text)
    status = db.Column(db.String(40), default="Abierta")


class NonConformity(db.Model):
    __tablename__ = "non_conformities"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    corrective_action = db.Column(db.Text)
    status = db.Column(db.String(40), default="Abierta")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    topic = db.Column(db.String(120))
    description = db.Column(db.Text)
    resource_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    status = db.Column(db.String(40), default="En progreso")
    score = db.Column(db.Float)
    completed_at = db.Column(db.DateTime)
    user = db.relationship("User")
    course = db.relationship("Course")


class Claim(db.Model):
    __tablename__ = "claims"
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"))
    customer = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(40), default="Abierto")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def seed_defaults():
    if User.query.count() == 0:
        admin = User(username="admin", email="admin@peruviam.pe",
                     full_name="Administrador", role="admin")
        admin.set_password("admin123")
        sup = User(username="supervisor", email="supervisor@peruviam.pe",
                   full_name="Supervisor de Calidad", role="supervisor")
        sup.set_password("super123")
        op = User(username="operario", email="operario@peruviam.pe",
                  full_name="Operario de Planta", role="operario")
        op.set_password("oper123")
        db.session.add_all([admin, sup, op])
        db.session.commit()

    if Course.query.count() == 0:
        topics = [
            ("Diagrama de Pareto", "Pareto", "Análisis de los pocos vitales."),
            ("Diagrama de Ishikawa", "Ishikawa", "Análisis causa-efecto."),
            ("Gráficas de Control", "SPC", "Control estadístico de procesos."),
            ("ISO 9000", "ISO", "Fundamentos de la norma."),
            ("Mejora Continua", "Kaizen", "Filosofía de mejora."),
            ("Calidad Total", "TQM", "Gestión de calidad total."),
        ]
        for t, topic, desc in topics:
            db.session.add(Course(title=t, topic=topic, description=desc))
        db.session.commit()

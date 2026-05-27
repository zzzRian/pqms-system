from app import db
from app.models import AuditLog

def log_action(user, action, detail=""):
    entry = AuditLog(user_id=user.id if user else None, action=action, detail=detail)
    db.session.add(entry)
    db.session.commit()

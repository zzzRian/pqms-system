from app import create_app, db
from app.models import seed_defaults

app = create_app()

with app.app_context():
    db.create_all()
    seed_defaults()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

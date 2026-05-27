import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    # Railway MySQL
    DB_USER = os.getenv("MYSQLUSER", "root")
    DB_PASSWORD = os.getenv("MYSQLPASSWORD", "")
    DB_HOST = os.getenv("MYSQLHOST", "localhost")
    DB_PORT = os.getenv("MYSQLPORT", "3306")
    DB_NAME = os.getenv("MYSQLDATABASE", "pqms_db")

    # Seguridad password
    DB_PASSWORD_SAFE = quote_plus(DB_PASSWORD)

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_SAFE}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        "app/static/uploads"
    )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

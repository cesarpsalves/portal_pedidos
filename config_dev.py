import os

class DevConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "notas_fiscais")
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

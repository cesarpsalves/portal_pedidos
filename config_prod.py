import os

class ProdConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "prod_secret_key")
    UPLOAD_FOLDER = "/opt/portal_pedidos/uploads/notas_fiscais"
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

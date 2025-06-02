import os


class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root@localhost/portal_pedidos"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "P@ulo2013"

    # Diretório onde serão salvas as notas fiscais anexadas
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "notas_fiscais")
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

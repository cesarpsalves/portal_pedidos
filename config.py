import os

class Config:
    # Banco de dados
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Chave de sessão / CSRF
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Pasta de upload (se você usar upload de arquivos em outro lugar)
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "notas_fiscais")
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

    # E-mail (Flask-Mail)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # OAuth Google (Flask-Dance)
    # Se você usar HTTPS no domínio real, pode remover 'OAUTHLIB_INSECURE_TRANSPORT'
    OAUTHLIB_INSECURE_TRANSPORT = False
    GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # Se quiser manter uma lista de domínios internos (autorizados), você
    # pode declará-la aqui:
    DOMINIOS_AUTORIZADOS = ("@kfp.com.br", "@kfp.net.br", "@grifcar.com.br")

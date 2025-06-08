# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # — Banco de dados —
    SQLALCHEMY_DATABASE_URI        = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://user:password@localhost/portal_pedidos"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # — Chave secreta de sessão/CSRF —
    SECRET_KEY = os.getenv("SECRET_KEY", "troque-por-uma-chave-secreta")

    # — Upload (se usar) —
    UPLOAD_FOLDER      = os.path.join(basedir, "uploads", "notas_fiscais")
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

    # — E-mail (Flask-Mail) —
    MAIL_SERVER         = os.getenv("MAIL_SERVER", "")
    MAIL_PORT           = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS        = os.getenv("MAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
    MAIL_USERNAME       = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD       = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = ("Portal Pedidos", MAIL_USERNAME)

    # — OAuth Google (Flask-Dance) —
    # Permite usar HTTP em dev; em produção garanta HTTPS e FLASK_ENV != "development"
    OAUTHLIB_INSECURE_TRANSPORT = (os.getenv("FLASK_ENV") == "development")
    GOOGLE_OAUTH_CLIENT_ID      = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_OAUTH_CLIENT_SECRET  = os.getenv("GOOGLE_CLIENT_SECRET", "")
    # Para centralizar o callback
    GOOGLE_OAUTH_REDIRECT_URI   = os.getenv(
        "GOOGLE_OAUTH_REDIRECT_URI",
        "/login/google/callback"
    )

    # — Segurança de Cookies —
    SESSION_COOKIE_SECURE   = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # — Domínios internos que auto-ativam conta —
    DOMINIOS_AUTORIZADOS = (
        "@kfp.com.br",
        "@kfp.net.br",
        "@grifcar.com.br",
    )

import os

class Config:
    # — Banco de dados —
    SQLALCHEMY_DATABASE_URI        = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # — Chave secreta de sessão/CSRF —
    SECRET_KEY = os.getenv("SECRET_KEY")

    # — Upload (se usar) —
    UPLOAD_FOLDER     = os.path.join(os.getcwd(), "uploads", "notas_fiscais")
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

    # — E-mail (Flask-Mail) —
    MAIL_SERVER         = os.getenv("MAIL_SERVER")
    MAIL_PORT           = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS        = (os.getenv("MAIL_USE_TLS", "True").lower() in ("true","1","yes"))
    MAIL_USERNAME       = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD       = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # — OAuth Google (Flask-Dance) —
    OAUTHLIB_INSECURE_TRANSPORT = False
    GOOGLE_OAUTH_CLIENT_ID      = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET  = os.getenv("GOOGLE_CLIENT_SECRET")

    # — ESSENCIAL: informa ao Flask que estamos em HTTPS em production —
    # SERVER_NAME          = "portal.pauloalves.dev"
    # PREFERRED_URL_SCHEME = "https"

    # — Faz com que o cookie de sessão só seja enviado em conexões reais HTTPS —
    SESSION_COOKIE_SECURE   = True
    # — Permite o OAuth funcionar com SameSite em redirecionamentos de terceiros (Google) —
    SESSION_COOKIE_SAMESITE = "Lax"

    # (Se quiser manter algum domínio “interno” para auto-ativar usuário:)
    DOMINIOS_AUTORIZADOS = ("@kfp.com.br", "@kfp.net.br", "@grifcar.com.br")

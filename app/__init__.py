# app/__init__.py

import os
from flask import Flask, current_app
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from datetime import datetime
from app.extensions import db, migrate, mail

# 1) Carrega as variáveis do .env assim que o pacote “app” for importado
load_dotenv()

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # 2) Carrega tudo do .env em app.config (NÃO use config_dev/config_prod aqui)
    app.config.from_mapping(os.environ)

    # 3) Traduz DATABASE_URL → SQLALCHEMY_DATABASE_URI
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("É preciso definir DATABASE_URL no seu .env")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # 4) Inicializa as extensões
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    # 5) Injeta o ano atual e current_app nos templates
    @app.context_processor
    def inject_ano():
        return {"ano": datetime.now().year}

    @app.context_processor
    def expose_current_app():
        return {"current_app": current_app}

    # ─── IMPORTAÇÃO DOS SEUS BLUEPRINTS ──────────────────────────────────────

    from app.routes.main         import main_bp
    from app.routes.auth         import auth_bp
    from app.routes.google_auth  import google_bp, google_auth_bp
    from app.routes.solicitacoes import solicitacoes_bp
    from app.routes.anexos       import anexos_bp
    from app.routes.admin        import admin_bp
    from app.routes.aprovacoes   import aprovacoes_bp
    from app.routes.compras      import compras_bp
    from app.routes.historico    import historico_bp
    from app.routes.recebimentos import recebimentos_bp

    # ─── REGISTRO DE BLUEPRINTS NA ORDEM CORRETA ────────────────────────────

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # → aqui dizemos ao Flask-Dance para montar “/login/google” e “/login/google/authorized”
    app.register_blueprint(google_bp,     url_prefix="/login")
    app.register_blueprint(google_auth_bp)  # o callback "/login/google/authorized"

    app.register_blueprint(solicitacoes_bp)
    app.register_blueprint(anexos_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(aprovacoes_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(historico_bp)
    app.register_blueprint(recebimentos_bp)

    return app

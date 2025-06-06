# app/__init__.py

import os
from flask import Flask, current_app
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix   # <– já estava aqui
from app.extensions import db, migrate, mail

# 1) Carrega o .env assim que importamos o pacote “app”
load_dotenv()

csrf = CSRFProtect()

def create_app():
    # 2) Cria a instância do Flask
    app = Flask(__name__)

    # 2a) Envolva o wsgi_app no ProxyFix para respeitar X-Forwarded-For/Proto
    #     Isso faz com que flask.url_for(..., _external=True) saiba usar “https://portal.pauloalves.dev”
    #     em vez de “http://127.0.0.1:8000”.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # 3) Carrega todas as variáveis de ambiente do sistema (ou seja, do .env) em app.config
    app.config.from_mapping(os.environ)

    # 4) Se não tiver “SQLALCHEMY_DATABASE_URI” em app.config, joga erro
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("É preciso definir DATABASE_URL no seu .env")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    # 5) Desliga track modifications (economiza recursos)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # 6) Aqui definimos o pool_pre_ping e pool_recycle para evitar “MySQL server has gone away”
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,   # adapte este número conforme o wait_timeout do seu MySQL
    }

    # 7) Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    # 8) Context processor para injetar o ano atual em todos os templates
    @app.context_processor
    def inject_ano():
        return {"ano": datetime.now().year}

    # 9) Context processor para expor `current_app` nos templates
    @app.context_processor
    def expose_current_app():
        return {"current_app": current_app}

    # ─────────────── REGISTRO DE BLUEPRINTS ────────────────

    # a) Rota principal (“home”, “/dashboard”, etc.)
    from app.routes.main import main_bp

    # b) Rotas de autenticação manual (login, logout, cadastro)
    from app.routes.auth import auth_bp

    # c) Rotas relacionadas ao Google OAuth (Flask-Dance)
    from app.routes.google_auth import google_bp, google_auth_bp

    # d) Outras partes do sistema
    from app.routes.solicitacoes   import solicitacoes_bp
    from app.routes.anexos        import anexos_bp
    from app.routes.admin         import admin_bp
    from app.routes.aprovacoes    import aprovacoes_bp
    from app.routes.compras       import compras_bp
    from app.routes.historico     import historico_bp
    from app.routes.recebimentos  import recebimentos_bp

    # ─── A ordem de registro importa ────────────────────────

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # **Importante**: o próprio make_google_blueprint (em google_auth.py) já define url_prefix="/login"
    app.register_blueprint(google_bp,      url_prefix="/login")
    # Registramos nossa rota de callback “/login/google/authorized”
    app.register_blueprint(google_auth_bp)

    # Finalmente, registre o resto dos blueprints:
    app.register_blueprint(solicitacoes_bp)
    app.register_blueprint(anexos_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(aprovacoes_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(historico_bp)
    app.register_blueprint(recebimentos_bp)

    return app

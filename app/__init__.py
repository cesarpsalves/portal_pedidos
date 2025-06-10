import os
from flask import Flask, current_app
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
from app.extensions import db, migrate, mail

# 1) Carrega o .env assim que importamos o pacote “app”
load_dotenv()

csrf = CSRFProtect()

def create_app():
    # 2) Cria a instância do Flask
    app = Flask(__name__)

    # 2a) Envolva o wsgi_app no ProxyFix para respeitar X-Forwarded-For/Proto
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # 3) Carrega variáveis de ambiente no config
    app.config.from_mapping(os.environ)

    # 4) Garante DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("É preciso definir DATABASE_URL no seu .env")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # 5) Ajustes de pool para MySQL
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # 6) Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    # 7) Context processors
    @app.context_processor
    def inject_ano():
        return {"ano": datetime.now().year}

    @app.context_processor
    def expose_current_app():
        return {"current_app": current_app}

    # ─────────────── REGISTRO DE BLUEPRINTS ────────────────

    # main
    from app.routes.main import main_bp
    # auth manual
    from app.routes.auth import auth_bp
    # google oauth (Flask-Dance)
    from app.routes.google_auth import google_bp, google_auth_bp
    # perfil do usuário
    from app.routes.profile import profile_bp
    # outras funcionalidades
    from app.routes.solicitacoes import solicitacoes_bp
    from app.routes.anexos        import anexos_bp
    from app.routes.admin         import admin_bp
    from app.routes.aprovacoes    import aprovacoes_bp
    from app.routes.compras       import compras_bp
    from app.routes.historico     import historico_bp
    from app.routes.recebimentos  import recebimentos_bp

    # registro
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(google_bp, url_prefix="/login")
    app.register_blueprint(google_auth_bp)
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(solicitacoes_bp)
    app.register_blueprint(anexos_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(aprovacoes_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(historico_bp)
    app.register_blueprint(recebimentos_bp)

    # ─────────────── REGISTRO DE FILTROS JINJA ────────────────
    from app.utils.filtros import registrar_filtros
    registrar_filtros(app)

    return app
